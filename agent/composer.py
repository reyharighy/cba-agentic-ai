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

    def get_punt_response_rationale(self, state: State) -> str:
        """
        Provide rationale to punt_response node.

        The rational is a base for the node to response produced by request_classification
        node in the previous process. Thus, it will help the generated response being less
        templated.
        """
        if state["request_classification"]:
            context_prompt: str = "\n\nThe rationale of why the user's request is not related to business analytics domain:\n"
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

    def get_data_unavailability_response_rationale(self, state: State) -> str:
        """
        Provide rationale to data_unavailability_response node.

        The rational is a base for the node to response produced by data_availability
        node in the previous process. Thus, it will help the response generated to be align 
        with contextual information of why the request can't be answered based on data.
        """
        if state["data_availability"]:
            context_prompt: str = "\n\nThe rationale of why the external database is unsupported to answer the user's request:\n"
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
            context_prompt += f"\nThe rationale of executed SQL query: {state["data_retrieval_planning"].rationale}"

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
        """
        if state["data_retrieval_execution"]:
            context_prompt: str = "\n\nThe feedback of why the data retrieval execution result on external database raises an error:\n"
            context_prompt += str(state["data_retrieval_execution"])

            return context_prompt

        raise ValueError(f"'data_retrieval_execution' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")
    
    def get_data_retrieval_observation_feedback(self, state: State) -> str:
        """
        Provides observational feedback explaining why retrieved data is insufficient for the user's analytical intent.
        """
        if state["data_retrieval_observation"]:
            context_prompt: str = "\n\nThe feedback of why the data retrieval execution result on external database is insufficient to answer the user's request:\n"
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
                    if table not in [table_name for table_name in schema]:
                        return ValueError(f"Unknown table: {table}")

                for column in columns:
                    if column not in [column["name"] for sublist in nested_columns for column in sublist]:
                        return ValueError(f"Unknown column: {column}")
            else:
                raise TypeError("value in key 'columns' of schema should be a type of dict")
        except ParseError as e:
            return ValueError(f"Invalid SQL Syntax: {e}")

