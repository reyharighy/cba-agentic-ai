"""
The composer is responsible for deriving and assembling contextual
information used by graph nodes before and after LLM inference.
It does not execute graph logic or control flow.

This module provides helper functions used by graph nodes to retrieve,
transform, and assemble contextual information.
"""
# standard
import sys
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    Union,
)

# third-party
import pandas as pd
import sqlglot
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)
from langgraph.runtime import Runtime
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from pandas.errors import EmptyDataError
from sqlglot import (
    exp,
    Expression,
    ParseError,
)

# internal
from .runtime import Context
from .state import State
from context.database import ContextManager
from context.datasets import working_dataset_path
from memory.database import MemoryManager
from memory.models import (
    ChatHistory,
    ChatHistoryShow,
    ShortMemory
)

class Composer:
    def __init__(self, context_manager: ContextManager, memory_manager: MemoryManager) -> None:
        """
        Initialize the composer with access to contextual runtime.
        """
        self.context_manager: ContextManager = context_manager
        self.memory_manager: MemoryManager = memory_manager

    def get_conversation_summary_list(self) -> str:
        """
        Construct a summarized view of prior conversation turns.

        The summary is derived from short-term memory and formatted as
        prompt-ready context to provide historical grounding for
        downstream LLM reasoning.
        """
        short_memories: List[ShortMemory] = self.memory_manager.index_short_memory()

        if short_memories:
            context_prompt: str = "\n\nConversation history summarized by turn number:"

            for short_memory in short_memories:
                context_prompt += f"\n[TURN-{short_memory.turn_num}]: {short_memory.summary}"

            return context_prompt

        return "\n\nThere is no conversation history."

    def get_relevant_conversation(self, state: State) -> Sequence:
        """
        Assemble conversation turns relevant to the current request.

        Relevant turns are selected based on intent comprehension results
        stored in the agent state and reconstructed as role-preserving
        LangChain message objects suitable for LLM input.
        """
        llm_input: Sequence = []

        if state["intent_comprehension"]:
            for turn_num in state["intent_comprehension"].relevant_turns:
                params: ChatHistoryShow = ChatHistoryShow(turn_num=int(turn_num))
                relevant_turn: List[ChatHistory] = self.memory_manager.show_chat_history(params)

                for chat in relevant_turn:
                    if chat.role == "Human":
                        llm_input += [HumanMessage(content=chat.content)]
                    else:
                        llm_input += [AIMessage(content=chat.content)]

        return llm_input

    def get_punt_response_feedback(self, state: State) -> str:
        """
        Provide feedback to punt_response node.

        The rational is a base for the node to response produced by request_classification
        node in the previous process. Thus, it will help the generated response being less
        templated.
        """
        if state["request_classification"]:
            context_prompt: str = "\n\nThe feedback why the user's request is not related to business analytics domain:\n"
            context_prompt += state["request_classification"].rationale

            return context_prompt

        raise ValueError(f"'request_classification' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_database_schema_info(self) -> str:
        """
        Expose external database schema information and sample values of each column.

        This context is used to inform analytical planning and query generation
        by describing available tables, columns, and structural metadata.
        """
        context_prompt: str = "\n\nThe external database schema and sample values in each columns::\n"
        context_prompt += repr(self.context_manager.inspect_external_database())

        return context_prompt

    def get_data_unavailability_response_feedback(self, state: State) -> str:
        """
        Provide feedback to data_unavailability_response node.

        The rational is a base for the node to response produced by data_availability
        node in the previous process. Thus, it will help the response generated to be align 
        with contextual information of why the request can't be answered based on data.
        """
        if state["data_availability"]:
            context_prompt: str = "\n\nThe feedback why the external database is unsupported to answer the user's request:\n"
            context_prompt += state["data_availability"].rationale

            return context_prompt

        raise ValueError(f"'data_availability' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_last_generated_sql_query(self, state: State) -> str:
        """
        Provide the SQL query used in the most recent data extraction.

        This context links analytical results back to their data provenance.
        """
        if state["data_retrieval_planning"]:
            context_prompt: str = "\n\nThe last generated SQL query used to extract data from external database into dataframe:\n"
            context_prompt += str(state["data_retrieval_planning"].sql_query)
            context_prompt += "\n\nThe reason why the generated SQL query is used to extract data from external database:\n"
            context_prompt += f"{state["data_retrieval_planning"].rationale}"

            return context_prompt

        raise ValueError(f"'data_retrieval_planning' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_dataframe_schema_info(self) -> str:
        """
        Describe schema information and sample values of the working dataset.

        The method inspects the dataset loaded into the analytical environment
        and summarizes column types along with representative values to guide
        analytical reasoning.
        """
        if not working_dataset_path.exists():
            working_dataset_path.touch()

        try:
            context_prompt: str = "\n\nDataframe schema and sample values in each columns:"
            col_value_dict: Dict[str, tuple[str, Any]] = {}
            dset_attrs: str = ""
            df: pd.DataFrame = pd.read_csv(working_dataset_path)

            for column in df.columns:
                if is_object_dtype(df[column]):
                    try:
                        df[column] = pd.to_datetime(df[column])
                    except Exception as _:
                        continue

            for column in df.columns:
                if is_numeric_dtype(df[column]) or is_datetime64_any_dtype(df[column]):
                    col_value_dict[column] = (str(df[column].dtype), df[column].unique()[:1])
                else:
                    col_value_dict[column] = (str(df[column].dtype), df[column].unique())

            for col_name, values in col_value_dict.items():
                dset_attrs += f"\n- {col_name} ({values[0]}): {list(str(value) for value in values[1])}"

            context_prompt += dset_attrs

            return context_prompt
        except EmptyDataError as _:
            return "\n\nThere is no dataframe object representation."

    def get_data_retrieval_execution_feedback(self, state: State) -> str:
        """
        Provides execution-level feedback context to guide query replanning after a SQL execution failure.

        The returned feedback supports error diagnosis and corrective sql query executed on the external database.
        """
        if state["data_retrieval_execution"]:
            context_prompt: str = "\n\nThe feedback why the data retrieval execution result on external database raises an error:\n"
            context_prompt += str(state["data_retrieval_execution"])

            return context_prompt

        raise ValueError(f"'data_retrieval_execution' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")
    
    def get_data_retrieval_observation_feedback(self, state: State) -> str:
        """
        Provides observational feedback explaining why retrieved data is insufficient for the user's analytical intent.
        """
        if state["data_retrieval_observation"]:
            context_prompt: str = "\n\nThe feedback why the data retrieval execution result on external database is insufficient to answer the user's request:\n"
            context_prompt += state["data_retrieval_observation"].rationale

            return context_prompt

        raise ValueError(f"'data_retrieval_observation' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def validate_sql_query(self, sql_query: str, schema: Dict[Literal["tables", "columns"], Union[List, Dict]]) -> Optional[ValueError]:
        """
        Validates a SQL query against syntax, safety constraints, and known database schema before execution.
        """
        try:
            tree: Expression = sqlglot.parse_one(sql_query)

            if forbidden := tree.find(exp.Delete, exp.Update, exp.Insert, exp.Drop):
                return ValueError(f"Forbidden SQL operation: {str(forbidden).split()[0]}")

            tables: List[str] = [table.name for table in tree.find_all(exp.Table)]
            columns: List[str] = [column.name for column in tree.find_all(exp.Column)]

            if isinstance(schema["columns"], Dict):
                nested_columns = [columns for columns in schema["columns"].values()]

                for table in tables:
                    if table not in schema["tables"]:
                        return ValueError(f"Unknown table: {table}")

                for column in columns:
                    if column not in [column["name"] for sublist in nested_columns for column in sublist]:
                        return ValueError(f"Unknown column: {column}")
            else:
                raise TypeError("value in key 'columns' of schema should be a type of dict")
        except ParseError as e:
            return ValueError(f"Invalid SQL Syntax: {e}")

    def get_analytical_python_code(self, state: State, runtime: Runtime[Context]) -> str:
        """
        Generate the executable Python code for sandbox execution.

        This method assembles the sandbox bootstrap code based on the analysis type and the purpose of analystic plan execution.
        """
        code: str = ""

        if state["analytical_planning"]:
            code += runtime.context.analytical_sandbox_bootstrap[state["analytical_planning"].analysis_type]

            for analytical_step in state["analytical_planning"].plan:
                code += '\n' + analytical_step.python_code + '\n'

            return code
        else:
            raise ValueError(f"'analytical_planning' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_analytical_plan(self, state: State, original: bool = False) -> str:
        """
        List the analytical plan that was generated.

        The output represents the structured plan used to guide sandbox execution and subsequent observation.
        """
        if state["analytical_planning"]:
            context_prompt: str = "\n\nThe step-by-step computational plan:"

            for analytical_step in state["analytical_planning"].plan:
                context_prompt += f"\n{analytical_step.number}. {analytical_step.rationale}" if not original else f"\n- {analytical_step}"

            return context_prompt

        raise ValueError(f"'analytical_planning' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_analytical_plan_execution_error(self, state: State) -> str:
        """
        Retrieve execution error details from the sandbox environment.

        The returned traceback supports error diagnosis and corrective planning during self-correction stage of analytical_plan node.
        """
        if state["analytical_plan_execution"] and state["analytical_plan_execution"].error:
            context_prompt: str = "\n\nThe traceback error logs from the sandbox environment:\n"
            context_prompt += state["analytical_plan_execution"].error.traceback

            return context_prompt

        raise ValueError(f"'analytical_plan_execution' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_analytical_plan_observation_feedback(self, state: State) -> str:
        """
        Retrieve the feedback produced during analytical plan execution result observation.

        The returned feedback supports corrective analytical planning that's been assesses as insufficient.
        """
        if state["analytical_plan_observation"]:
            context_prompt: str = "\n\nThe feedback why the analytical plan execution result is insufficient to answer the user's request:\n"
            context_prompt += state["analytical_plan_observation"].rationale

            return context_prompt

        raise ValueError(f"'analytical_plan_observation' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_analytical_plan_execution_result(self, state: State) -> str:
        """
        Retrieve standard output produced by sandbox execution.

        This information reflects the observable results of analytical plan execution and is used during result evaluation.
        """
        if state["analytical_plan_execution"]:
            context_prompt: str = "\n\nThe execution logs from the sandbox environment:\n"
            context_prompt += str(state["analytical_plan_execution"].logs.stdout[0])

            return context_prompt

        raise ValueError(f"'analytical_plan_execution' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_analytical_plan_observation_result(self, state: State) -> str:
        """
        Retrieve the rationale produced during analytical plan execution result observation.

        The returned rationale supports the analytical_result to produce the final response after execution the analytical plan.
        """
        if state["analytical_plan_observation"]:
            context_prompt: str = "\n\nThe observation result on the execution output of the analytical plan:\n"
            context_prompt += state["analytical_plan_observation"].rationale

            return context_prompt

        raise ValueError(f"'analytical_plan_observation' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_infographic_requirement_rationale(self, state: State) -> str:
        """
        Retrieve the rationale why the infographic is necessary to enhance the generated analytical results.

        This information helps guide the infographic_planning to determine the visual intent.
        """
        context_prompt: str = ""

        if state["infographic_requirement"]:
            context_prompt += "\n\nThe reason why the analysis result requires infographic plot to communicates more clearly:\n"
            context_prompt += state["infographic_requirement"].rationale

            return context_prompt

        raise ValueError(f"'infographic_requirement' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_infographic_plan(self, state: State) -> str:
        """
        List the infographic plan that was generated.

        The output represents the plot plan used to guide sandbox execution and subsequent observation.
        """
        if state["infographic_planning"]:
            context_prompt: str = "\n\nInfographic plan that was generated previously:"

            for plot in state["infographic_planning"].plot_plan:
                context_prompt += f"\n- {plot}"

            return context_prompt

        raise ValueError(f"'infographic_planning' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_infographic_plan_execution_error(self, state: State) -> str:
        """
        Retrieve execution error details from the sandbox environment.

        The returned traceback supports error diagnosis and corrective planning during self-correction stage of infographic_planning node.
        """
        if state["infographic_plan_execution"] and state["infographic_plan_execution"].error:
            context_prompt: str = "\n\nThe traceback error logs from the sandbox environment when execution infographic plan:\n"
            context_prompt += state["infographic_plan_execution"].error.traceback

            return context_prompt

        raise ValueError(f"'infographic_plan_execution' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_infographic_plan_observation_feedback(self, state: State) -> str:
        """
        Retrieve the feedback produced during analytical plan execution result observation.

        The returned feedback supports corrective analytical planning that's been assesses as insufficient.
        """
        if state["infographic_plan_observation"]:
            context_prompt: str = "\n\nThe feedback why the infographic plan execution result is insufficient to enhance the analytical result:\n"
            context_prompt += state["infographic_plan_observation"].rationale

            return context_prompt

        raise ValueError(f"'infographic_plan_observation' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_infographic_python_code(self, state: State, runtime: Runtime[Context]) -> str:
        """
        Generate the executable Python code for sandbox execution.

        This method assembles the sandbox bootstrap code necessary for the code that executes a process of creating an infographic.
        """
        code: str = ""

        if state["infographic_planning"]:
            code += runtime.context.infographic_sandbox_bootstrap

            for plot in state["infographic_planning"].plot_plan:
                code += '\n' + plot.python_code + '\n'

            return code
        else:
            raise ValueError(f"'infographic_planning' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")
