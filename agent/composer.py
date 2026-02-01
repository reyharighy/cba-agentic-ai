# pyright: reportPrivateUsage=false
# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false

# standard
import sys
from typing import (
    Any,
    cast,
)
from uuid import UUID

# third-party
import pandas as pd
import sqlglot
from e2b_code_interpreter.code_interpreter_sync import (
    Sandbox,
)
from groq import BadRequestError
from langchain_core.language_models import (
    BaseChatModel,
    LanguageModelInput,
)
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    AnyMessage,
)
from langchain_core.runnables import Runnable
from langchain_core.exceptions import OutputParserException
from langgraph.runtime import Runtime
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from pandas.errors import EmptyDataError
from pydantic import BaseModel
from sqlglot import (
    exp,
    Expression,
    ParseError,
)

# internal
from .runtime import Context
from .state import State
from context.database import ContextManager
from context.datasets import dataset_file_path
from memory.database import MemoryManager
from memory.models import (
    ChatHistory,
    ChatHistoryShow,
    ShortMemory,
)


class Composer:
    def __init__(self, context_manager: ContextManager, memory_manager: MemoryManager) -> None:
        """
        Initialize the composer with access to contextual runtime and memory management.
        """
        self.context_manager: ContextManager = context_manager
        self.memory_manager: MemoryManager = memory_manager

    def get_conversation_summary_list(self) -> str:
        """
        Retrieve a summary list of past conversations from short-term memory.
        """
        short_memories: list[ShortMemory] = self.memory_manager.index_short_memory()

        if short_memories:
            context_prompt: str = "\n\nConversation history summary:\n"

            for short_memory in short_memories:
                context_prompt += f"\n[TURN-{short_memory.turn_num}]: {short_memory.summary}"

            return context_prompt

        return "\n\nNo conversation history available."

    def prepare_invocation(
        self,
        system_message: SystemMessage,
        state: State,
        language_model: BaseChatModel,
        schema: type[BaseModel] | None = None,
        include_conversation: bool = False,
    ) -> tuple[Runnable[LanguageModelInput, dict[Any, Any] | BaseModel] | BaseChatModel, list[AnyMessage]]:
        """
        Prepare the language model invocation with system message and state.
        """
        if schema:
            llm = cast(
                typ=Runnable[LanguageModelInput, dict[Any, Any] | BaseModel],
                val=language_model.with_structured_output(
                    schema=schema,
                    method="json_schema",
                ),
            )

            llm = llm.with_retry(
                retry_if_exception_type=(
                    BadRequestError,
                    OutputParserException,
                ),
                stop_after_attempt=3,
            )
        else:
            llm = language_model

        if state["context_distillation"] and not include_conversation:
            content: str = cast(str, state["context_distillation"].content)
            human_message: HumanMessage = HumanMessage(content)
            llm_input: list[AnyMessage] = [system_message, human_message]
        else:
            llm_input: list[AnyMessage] = self.__prepare_language_model_message_input(
                system_message=system_message,
                state=state,
                include_conversation=include_conversation,
            )

        if state["analytical_result"] and state["next_node"] != "summarization":
            llm_input.extend([state["analytical_result"]])

        return (llm, llm_input)

    def __prepare_language_model_message_input(
        self, system_message: SystemMessage, state: State, include_conversation: bool = False
    ) -> list[AnyMessage]:
        """
        Prepare the language model message input with system message and state.
        """
        llm_input: list[AnyMessage] = [system_message]

        if include_conversation:
            llm_input.extend(self.__get_relevant_conversation(state))

        llm_input.extend(state["messages"])

        return llm_input

    def __get_relevant_conversation(self, state: State) -> list[AnyMessage]:
        """
        Retrieve relevant past conversations based on intent comprehension.
        """
        llm_input: list[AnyMessage] = []

        if state["intent_comprehension"]:
            for turn_num in state["intent_comprehension"].relevant_turns:
                params: ChatHistoryShow = ChatHistoryShow(turn_num=int(turn_num))
                relevant_turn: list[ChatHistory] = self.memory_manager.show_chat_history(params)

                for chat in relevant_turn:
                    if chat.role == "Human":
                        llm_input.extend([HumanMessage(content=chat.content)])
                    else:
                        llm_input.extend([AIMessage(content=chat.content)])

        return llm_input

    def get_punt_response_feedback(self, state: State) -> str:
        """
        Retrieve feedback for punt response based on request classification.
        """
        if state["request_classification"]:
            context_prompt: str = "\n\nFeedback why the user's request cannot be handled with the external database: "
            context_prompt += state["request_classification"].rationale

            return context_prompt

        raise ValueError(
            f"'request_classification' state must not be empty in '{sys._getframe(1).f_code.co_name}' node"
        )

    def get_database_schema_info(self) -> str:
        """
        Retrieve the external database schema information.
        """
        context_prompt: str = "\n\nExternal database schema with tables and their respective column specifications:"
        schema: dict[str, list[dict[str, Any]]] = self.context_manager.inspect_external_database()

        for table_name, column_item in schema.items():
            context_prompt += f"\n- Table '{table_name}' has following column specifications:"

            for column in column_item:
                context_prompt += f"\n\t- Column '{column['name']}' of type '{column['type']}'. "
                context_prompt += f"It describes about '{column['comment']}'. " if column.get("comment", None) else ""
                context_prompt += (
                    f"It has sample value(s) such as `{column['sample_values']}`. "
                    if column.get("sample_values", None)
                    else ""
                )
                context_prompt += (
                    f"It has the earliest timestamp value as `{column['earliest_timestamp']}`. "
                    if column.get("earliest_timestamp", None)
                    else ""
                )
                context_prompt += (
                    f"It has the latest timestamp value as `{column['latest_timestamp']}`. "
                    if column.get("latest_timestamp", None)
                    else ""
                )

        return context_prompt

    def get_data_unavailability_response_feedback(self, state: State) -> str:
        """
        Retrieve feedback for data unavailability response based on data availability.
        """
        if state["data_availability"]:
            context_prompt: str = "\n\nFeedback why the required data is unavailable in the external database: "
            context_prompt += state["data_availability"].rationale

            return context_prompt

        raise ValueError(f"'data_availability' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_data_retrieval_plan(self, state: State) -> str:
        """
        Retrieve the data retrieval plan including SQL query and rationale.
        """
        if state["data_retrieval_plan"]:
            context_prompt: str = "\n\nSQL query generated to extract data from external database: "
            context_prompt += str(state["data_retrieval_plan"].sql_query)

            context_prompt += "\n\nRationale for the data retrieval plan: "
            context_prompt += f"{state['data_retrieval_plan'].rationale}"
            return context_prompt

        raise ValueError(f"'data_retrieval_plan' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_dataframe_schema_info(self) -> str:
        """
        Retrieve the dataframe schema from the dataset CSV file.
        """
        if not dataset_file_path.exists():
            dataset_file_path.touch()

        try:
            context_prompt: str = "\n\nDataframe schema with columns and sample value(s): "
            col_value_dict: dict[str, tuple[str, Any]] = {}
            dset_attrs: str = ""
            df: pd.DataFrame = pd.read_csv(dataset_file_path)

            for column in df.columns:
                if is_object_dtype(df[column]):
                    try:
                        df[column] = pd.to_datetime(df[column])
                    except Exception as _:
                        continue

            for column in df.columns:
                try:
                    # Even if data_retrieval_plan is set to ignore identifiers,
                    # we must implement a manual override to ensure they are strictly excluded.
                    UUID(df[column].iloc[0])
                except Exception as _:
                    if is_datetime64_any_dtype(df[column]):
                        col_value_dict[column] = (str(df[column].dtype), df[column].unique()[:1])
                    elif is_numeric_dtype(df[column]):
                        col_value_dict[column] = (str(df[column].dtype), df[column].unique()[:2])
                    else:
                        col_value_dict[column] = (str(df[column].dtype), df[column].unique())

            for col_name, values in col_value_dict.items():
                dset_attrs += f"\n- {col_name} ({values[0]}): {list(str(value) for value in values[1])}"

            context_prompt += dset_attrs

            return context_prompt
        except EmptyDataError as _:
            return "\n\nNo dataframe schema information available."

    def get_data_retrieval_plan_execution_feedback(self, state: State) -> str:
        """
        Retrieve feedback for data retrieval plan execution errors.
        """
        if state["data_retrieval_plan_execution"]:
            context_prompt: str = "\n\nFeedback on the data retrieval execution from external database: "
            context_prompt += str(state["data_retrieval_plan_execution"])

            return context_prompt

        raise ValueError(
            f"'data_retrieval_plan_execution' state must not be empty in '{sys._getframe(1).f_code.co_name}' node"
        )

    def get_data_retrieval_plan_observation_feedback(self, state: State) -> str:
        """
        Retrieve feedback for data retrieval plan observation.
        """
        if state["data_retrieval_plan_observation"]:
            context_prompt: str = "\n\nFeedback why the data retrieval result is insufficient: "
            context_prompt += state["data_retrieval_plan_observation"].rationale

            return context_prompt

        raise ValueError(
            f"'data_retrieval_plan_observation' state must not be empty in '{sys._getframe(1).f_code.co_name}' node"
        )

    def validate_sql_query(self, sql_query: str, schema: dict[str, list[dict[str, Any]]]) -> ValueError | None:
        """
        Validate the SQL query against the provided database schema.
        """
        try:
            tree: Expression = sqlglot.parse_one(sql_query)

            if forbidden := tree.find(exp.Delete, exp.Update, exp.Insert, exp.Drop):
                return ValueError(f"Forbidden SQL operation: {str(forbidden).split()[0]}")

            tables: list[str] = [table.name for table in tree.find_all(exp.Table)]
            columns: list[str] = [column.name for column in tree.find_all(exp.Column)]

            for table in tables:
                if table not in schema.keys():
                    return ValueError(f"Unknown table: {table}")

            for column in columns:
                if column not in [col["name"] for col_list in schema.values() for col in col_list]:
                    return ValueError(f"Unknown column: {column}")
        except ParseError as e:
            return ValueError(f"Invalid SQL Syntax: {e}")

    def prepare_sandbox_environment(self) -> Sandbox:
        """
        Prepare the sandbox environment with the dataset CSV file.
        """
        sandbox: Sandbox = Sandbox.create()

        with open(dataset_file_path, "rb") as dataset:
            sandbox.files.write("dataset.csv", dataset.read())

        return sandbox

    def get_analytical_python_code(self, state: State, runtime: Runtime[Context]) -> str:
        """
        Retrieve the analytical Python code including bootstrap.
        """
        if state["analytical_plan"]:
            code: str = runtime.context.analytical_sandbox_bootstrap[state["analytical_plan"].analysis_type]

            for analytical_step in state["analytical_plan"].plan:
                for line in analytical_step.python_code.replace("\\n", "\n").replace("\\t", "\t").split("\n"):
                    code += "\n" + line + "\n"

            return code

        raise ValueError(f"'analytical_plan' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_analytical_plan(self, state: State, original: bool = False) -> str:
        """
        Retrieve the analytical plan with step-by-step rationale.
        """
        if state["analytical_plan"]:
            context_prompt: str = "\n\nAnalytical plan that was generated previously: "

            for analytical_step in state["analytical_plan"].plan:
                context_prompt += (
                    f"\n{analytical_step.number}. {analytical_step.rationale}"
                    if not original
                    else f"\n- {analytical_step}"  # Still not optimized for original structure
                )

            return context_prompt

        raise ValueError(f"'analytical_plan' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_analytical_plan_execution_feedback(self, state: State) -> str:
        """
        Retrieve feedback for analytical plan execution errors.
        """
        if state["analytical_plan_execution"] and state["analytical_plan_execution"].error:
            context_prompt: str = "\n\nTraceback error logs from the sandbox environment: "
            context_prompt += state["analytical_plan_execution"].error.traceback

            return context_prompt

        raise ValueError(
            f"'analytical_plan_execution' state must not be empty in '{sys._getframe(1).f_code.co_name}' node"
        )

    def get_analytical_plan_observation_feedback(self, state: State) -> str:
        """
        Retrieve feedback for analytical plan observation.
        """
        if state["analytical_plan_observation"]:
            context_prompt: str = "\n\nFeedback why the analytical plan execution result is insufficient: "
            context_prompt += state["analytical_plan_observation"].rationale

            return context_prompt

        raise ValueError(
            f"'analytical_plan_observation' state must not be empty in '{sys._getframe(1).f_code.co_name}' node"
        )

    def get_analytical_plan_execution_result(self, state: State) -> str:
        """
        Retrieve the analytical plan execution result logs.
        """
        if state["analytical_plan_execution"]:
            context_prompt: str = "\n\nExecution output logs of the analytical plan: "
            context_prompt += str(state["analytical_plan_execution"].logs.stdout[0])

            return context_prompt

        raise ValueError(
            f"'analytical_plan_execution' state must not be empty in '{sys._getframe(1).f_code.co_name}' node"
        )

    def get_analytical_plan_observation_result(self, state: State) -> str:
        """
        Retrieve the analytical plan observation rationale.
        """
        if state["analytical_plan_observation"]:
            context_prompt: str = "\n\nObservation on the analytical plan execution result: "
            context_prompt += state["analytical_plan_observation"].rationale

            return context_prompt

        raise ValueError(
            f"'analytical_plan_observation' state must not be empty in '{sys._getframe(1).f_code.co_name}' node"
        )

    def get_infographic_requirement_rationale(self, state: State) -> str:
        """
        Retrieve the rationale for infographic requirement.
        """
        if state["infographic_requirement"]:
            context_prompt: str = "\n\nRationale for the infographic requirement: "
            context_prompt += state["infographic_requirement"].rationale

            return context_prompt

        raise ValueError(
            f"'infographic_requirement' state must not be empty in '{sys._getframe(1).f_code.co_name}' node"
        )

    def get_infographic_plan(self, state: State) -> str:
        """
        Retrieve the infographic plan with rationale.
        """
        if state["infographic_plan"]:
            context_prompt: str = "\n\nInfographic plan that was generated to answer current request: "
            context_prompt += str(state["infographic_plan"])

            return context_prompt

        raise ValueError(
            f"'infographic_plan' state must not be empty in '{sys._getframe(1).f_code.co_name}' node if infographic is required"
        )

    def get_infographic_plan_execution_feedback(self, state: State) -> str:
        """
        Retrieve feedback for infographic plan execution errors.
        """
        if state["infographic_plan_execution"] and state["infographic_plan_execution"].error:
            context_prompt: str = "\n\nTraceback error logs from the sandbox environment: "
            context_prompt += state["infographic_plan_execution"].error.traceback

            return context_prompt

        raise ValueError(
            f"'infographic_plan_execution' state must not be empty in '{sys._getframe(1).f_code.co_name}' node"
        )

    def get_infographic_plan_observation_feedback(self, state: State) -> str:
        """
        Retrieve feedback for infographic plan observation.
        """
        if state["infographic_plan_observation"]:
            context_prompt: str = "\n\nFeedback why the infographic plan execution result is insufficient: "
            context_prompt += state["infographic_plan_observation"].rationale

            return context_prompt

        raise ValueError(
            f"'infographic_plan_observation' state must not be empty in '{sys._getframe(1).f_code.co_name}' node"
        )

    def get_infographic_python_code(self, state: State, runtime: Runtime[Context], on_sandbox: bool = False) -> str:
        """
        Retrieve the infographic Python code including bootstrap.
        """
        if state["infographic_plan"]:
            code: str = runtime.context.infographic_sandbox_bootstrap

            for line in state["infographic_plan"].python_code.replace("\\n", "\n").replace("\\t", "\t").split("\n"):
                code += "\n" + line if line != "fig" else "" + "\n"

            code += "\n_ = None" if on_sandbox else ""

            return code

        raise ValueError(f"'infographic_plan' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")
