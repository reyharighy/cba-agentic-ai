# pyright: reportPrivateUsage=false
# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false

# standard
from typing import (
    Any,
    cast,
)
from uuid import UUID

# third-party
import pandas as pd
import sqlglot
from e2b_code_interpreter.code_interpreter_sync import Sandbox, Execution, ExecutionError
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

from language_model.schema.structured_output import (
    AnalyticalPlan,
    AnalyticalPlanObservation,
    DataAvailability,
    DataRetrievalPlan,
    DataRetrievalPlanObservation,
    InfographicPlan,
    InfographicPlanObservation,
    InfographicRequirement,
    RequestClassification,
)

# internal
from .state import State
from .runtime import Context
from context import ContextManager
from context.datasets import dataset_file_path, unlink_dataset_file
from memory import MemoryManager
from memory.models import (
    ChatHistoryCreate,
    ChatHistoryShow,
    ShortMemoryCreate,
)

_SQL_VALIDATION_DIALECT: str = "postgres"

_NON_READ_SQL_EXPRESSIONS: tuple[type[Expression], ...] = (
    exp.Delete,
    exp.Update,
    exp.Insert,
    exp.Create,
    exp.Alter,
    exp.Drop,
    exp.TruncateTable,
    exp.Merge,
    exp.Copy,
    exp.Command,
    exp.Analyze,
    exp.Grant,
    exp.Revoke,
    exp.Set,
    exp.Transaction,
    exp.Commit,
    exp.Rollback,
)

def _unwrap_query_root(expression: Expression) -> Expression:
    current: Expression = expression

    while isinstance(current, (exp.Subquery, exp.Paren)):
        current = current.this

    return current

def _read_only_root_violation(tree: Expression) -> str | None:
    root: Expression = _unwrap_query_root(tree)

    if isinstance(root, (exp.Select, exp.Union)):
        return None

    return f"only read-only SELECT queries are allowed (got {type(root).__name__})"

def _non_read_ast_violation(tree: Expression) -> str | None:
    if forbidden := tree.find(*_NON_READ_SQL_EXPRESSIONS):
        return f"forbidden non read-only SQL ({type(forbidden).__name__})"

    return None

def _select_into_violation(tree: Expression) -> str | None:
    for select in tree.find_all(exp.Select):
        if select.args.get("into"):
            return "SELECT ... INTO is not allowed (creates a database object)"

    return None


class Composer:
    def __init__(
        self, context_manager: ContextManager, memory_manager: MemoryManager, language_model: BaseChatModel
    ) -> None:
        """
        Initialize the composer with access to contextual runtime and memory management.
        """
        self.context_manager: ContextManager = context_manager
        self.memory_manager: MemoryManager = memory_manager
        self.language_model: BaseChatModel = language_model

    def get_conversation_summary_list(self) -> str:
        """
        Retrieve a summary list of past conversations from short-term memory.
        """
        context_prompt: str = "\n\nConversation history summary:\n"

        for short_memory in self.memory_manager.index_short_memory():
            context_prompt += f"\n[TURN-{short_memory.turn_num}]: {short_memory.summary}"

        return context_prompt

    def get_runnable_with_input(
        self,
        state: State,
        system_message: SystemMessage,
        schema: type[BaseModel] | None = None,
    ) -> tuple[Runnable[LanguageModelInput, dict[Any, Any] | BaseModel] | BaseChatModel, list[AnyMessage]]:
        """
        Prepare the runnable language model and its message input.
        """
        if schema:
            llm = cast(
                typ=Runnable[LanguageModelInput, dict[Any, Any] | BaseModel],
                val=self.language_model.with_structured_output(
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
            llm = self.language_model

        llm_input: list[AnyMessage] = [system_message]

        if state["context_distillation"] and not (
            cast(str, state["current_node"]).endswith("_response")
            or cast(str, state["current_node"]).endswith("_result")
        ):
            llm_input.extend([HumanMessage(state["context_distillation"].content)])
        else:
            if state["intent_comprehension"]:
                for turn_num in state["intent_comprehension"].relevant_turns:
                    params: ChatHistoryShow = ChatHistoryShow(turn_num=int(turn_num))

                    for chat in self.memory_manager.show_chat_history(params):
                        llm_input.extend(
                            [HumanMessage(content=chat.content)]
                            if chat.role == "human"
                            else [AIMessage(content=chat.content)]
                        )

            llm_input.extend(state["messages"])

        if state["analytical_result"] and state["current_node"] != "summarization":
            llm_input.extend([state["analytical_result"]])

        return (llm, llm_input)

    def get_punt_response_feedback(self, state: State) -> str:
        """
        Retrieve feedback for punt response based on request classification.
        """
        context_prompt: str = "\n\nFeedback why the user's request cannot be handled with the external database: "
        context_prompt += cast(RequestClassification, state["request_classification"]).rationale

        return context_prompt

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
        context_prompt: str = "\n\nFeedback why the required data is unavailable in the external database: "
        context_prompt += cast(DataAvailability, state["data_availability"]).rationale

        return context_prompt

    def get_data_retrieval_plan(self, state: State) -> str:
        """
        Retrieve the data retrieval plan including SQL query and rationale.
        """
        context_prompt: str = "\n\nData retrieval plan that was generated to answer current request: "
        context_prompt += str(cast(DataRetrievalPlan, state["data_retrieval_plan"]))

        return context_prompt

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
        context_prompt: str = "\n\nFeedback on the data retrieval execution from external database: "
        context_prompt += str(state["data_retrieval_plan_execution"])

        return context_prompt

    def get_data_retrieval_plan_observation_feedback(self, state: State) -> str:
        """
        Retrieve feedback for data retrieval plan observation.
        """
        context_prompt: str = "\n\nFeedback why the data retrieval result is insufficient: "
        context_prompt += cast(DataRetrievalPlanObservation, state["data_retrieval_plan_observation"]).rationale

        return context_prompt

    def get_data_retrieval_failure_summary(self, state: State) -> str:
        """
        Build a context prompt from the accumulated data retrieval failure history.
        """
        failure_history: list[str] = state["data_retrieval_failure_history"]
        failure_log: str = "\n".join(f"- Attempt {i + 1}: {f}" for i, f in enumerate(failure_history))

        return f"\n\nFailure log:\n{failure_log}"

    def get_analytical_python_code(self, state: State, runtime: Runtime[Context]) -> str:
        """
        Retrieve the analytical Python code including bootstrap.
        """
        analysis_plan: AnalyticalPlan = cast(AnalyticalPlan, state["analytical_plan"])
        code: str = runtime.context.analytical_sandbox_bootstrap[analysis_plan.analysis_type]

        for analytical_step in analysis_plan.plan:
            for line in analytical_step.python_code.replace("\\n", "\n").replace("\\t", "\t").split("\n"):
                code += "\n" + line + "\n"

        return code

    def get_analytical_plan(self, state: State, original: bool = False) -> str:
        """
        Retrieve the analytical plan with step-by-step rationale.
        """
        context_prompt: str = "\n\nAnalytical plan that was generated previously: "

        for analytical_step in cast(AnalyticalPlan, state["analytical_plan"]).plan:
            context_prompt += (
                f"\n{analytical_step.number}. {analytical_step.rationale}" if not original else f"\n- {analytical_step}"
            )

        return context_prompt

    def get_analytical_plan_execution_feedback(self, state: State) -> str:
        """
        Retrieve feedback for analytical plan execution errors.
        """
        context_prompt: str = "\n\nTraceback error logs from the sandbox environment: "
        context_prompt += cast(ExecutionError, cast(Execution, state["analytical_plan_execution"]).error).traceback

        return context_prompt

    def get_analytical_plan_observation_feedback(self, state: State) -> str:
        """
        Retrieve feedback for analytical plan observation.
        """
        context_prompt: str = "\n\nFeedback why the analytical plan execution result is insufficient: "
        context_prompt += cast(AnalyticalPlanObservation, state["analytical_plan_observation"]).rationale

        return context_prompt

    def get_analytical_plan_execution_result(self, state: State) -> str:
        """
        Retrieve the analytical plan execution result logs.
        """
        context_prompt: str = "\n\nExecution output logs of the analytical plan: "
        context_prompt += cast(Execution, state["analytical_plan_execution"]).logs.stdout[0]

        return context_prompt

    def get_analytical_plan_observation_result(self, state: State) -> str:
        """
        Retrieve the analytical plan observation rationale.
        """
        context_prompt: str = "\n\nObservation on the analytical plan execution result: "
        context_prompt += cast(AnalyticalPlanObservation, state["analytical_plan_observation"]).rationale

        return context_prompt

    def get_infographic_requirement_rationale(self, state: State) -> str:
        """
        Retrieve the rationale for infographic requirement.
        """
        context_prompt: str = "\n\nRationale for the infographic requirement: "
        context_prompt += cast(InfographicRequirement, state["infographic_requirement"]).rationale

        return context_prompt

    def get_infographic_plan(self, state: State) -> str:
        """
        Retrieve the infographic plan with rationale.
        """
        context_prompt: str = "\n\nInfographic plan that was generated to answer current request: "
        context_prompt += str(cast(InfographicPlan, state["infographic_plan"]))

        return context_prompt

    def get_infographic_plan_execution_feedback(self, state: State) -> str:
        """
        Retrieve feedback for infographic plan execution errors.
        """
        context_prompt: str = "\n\nTraceback error logs from the sandbox environment: "
        context_prompt += cast(ExecutionError, cast(Execution, state["infographic_plan_execution"]).error).traceback

        return context_prompt

    def get_infographic_plan_observation_feedback(self, state: State) -> str:
        """
        Retrieve feedback for infographic plan observation.
        """
        context_prompt: str = "\n\nFeedback why the infographic plan execution result is insufficient: "
        context_prompt += cast(InfographicPlanObservation, state["infographic_plan_observation"]).rationale

        return context_prompt

    def get_infographic_python_code(self, state: State, runtime: Runtime[Context], on_sandbox: bool = False) -> str:
        """
        Retrieve the infographic Python code including bootstrap.
        """
        code: str = runtime.context.infographic_sandbox_bootstrap

        for line in (
            cast(InfographicPlan, state["infographic_plan"])
            .python_code.replace("\\n", "\n")
            .replace("\\t", "\t")
            .split("\n")
        ):
            code += "\n" + line if line != "fig" else "" + "\n"

        code += "\n_ = None" if on_sandbox else ""

        return code

    # Should the following method be part of Composer class?

    def validate_sql_query(self, state: State) -> ValueError | None:
        """
        Validate the SQL query against the provided database schema.
        """
        try:
            sql_query: str = cast(DataRetrievalPlan, state["data_retrieval_plan"]).sql_query.strip()

            if not sql_query:
                return ValueError("SQL query is empty")

            parsed: list[Expression | None] = sqlglot.parse(sql_query, dialect=_SQL_VALIDATION_DIALECT)
            statements: list[Expression] = [s for s in parsed if s is not None]

            if len(statements) != 1:
                return ValueError("Exactly one SQL statement is required (multiple statements are not allowed)")

            tree: Expression = statements[0]

            if msg := _read_only_root_violation(tree):
                return ValueError(msg)
            if msg := _non_read_ast_violation(tree):
                return ValueError(msg)
            if msg := _select_into_violation(tree):
                return ValueError(msg)

            tables: list[str] = [table.name for table in tree.find_all(exp.Table)]
            columns: list[str] = [column.name for column in tree.find_all(exp.Column)]
            schema: dict[str, list[dict[str, Any]]] = self.context_manager.inspect_external_database()

            for table in tables:
                if table not in schema.keys():
                    return ValueError(f"Unknown table: {table}")

            for column in columns:
                if column not in [col["name"] for col_list in schema.values() for col in col_list]:
                    return ValueError(f"Unknown column: {column}")

        except ParseError as e:
            return ValueError(f"Invalid SQL Syntax: {e}")

    def extract_external_database(self, state: State) -> ValueError | None:
        """
        Extract data from external database based on the provided SQL statement and save it to a CSV file.
        """
        return self.context_manager.extract_external_database(
            cast(DataRetrievalPlan, state["data_retrieval_plan"]).sql_query
        )

    def prepare_sandbox_environment(self) -> Sandbox:
        """
        Prepare the sandbox environment with the dataset CSV file.
        """
        sandbox: Sandbox = Sandbox.create()

        with open(dataset_file_path, "rb") as dataset:
            sandbox.files.write("dataset.csv", dataset.read())

        return sandbox

    def save_current_interaction(self, state: State, llm_output: AIMessage, turn_num: int) -> None:
        """
        Save the current interaction including messages and short-term memory summary.
        """
        for message in state["messages"]:
            create_chat_history_params: ChatHistoryCreate = ChatHistoryCreate(
                turn_num=turn_num,
                role="human" if message.type == "human" else "ai",
                content=cast(str, message.content),
            )

            self.memory_manager.store_chat_history(create_chat_history_params())

        create_short_memory_params: ShortMemoryCreate = ShortMemoryCreate(
            turn_num=turn_num,
            summary=cast(str, llm_output.content),
        )

        self.memory_manager.store_short_memory(create_short_memory_params())

        unlink_dataset_file()
