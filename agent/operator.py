"""
Operational utilities for graph.

This module provides helper functions used by graph nodes to retrieve,
transform, and assemble contextual information.
"""
# standard
import sys
from typing import (
    Any,
    Dict,
    List,
    Sequence,
)

# third-party
import pandas as pd
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

class Operator:
    def __init__(self, context_manager: ContextManager, memory_manager: MemoryManager) -> None:
        """
        Initialize the operator with access to persistent storage.
        """
        self.context_manager: ContextManager = context_manager
        self.memory_manager: MemoryManager = memory_manager

    def get_conversation_summary(self) -> str:
        """
        Provide a summarized representation of prior conversation turns.

        The summary is derived from stored short-term memory and is intended
        to supply historical context for downstream reasoning steps.
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
        Retrieve message history relevant to the current request.

        This method reconstructs selected conversation turns based on intent
        analysis results, preserving speaker roles for accurate LLM context.
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

    def get_database_schema_and_sample_values(self) -> str:
        """
        Expose external database schema information.

        This context is used to inform analytical planning and query generation
        by describing available tables, columns, and structural metadata.
        """
        context_prompt: str = "\n\nThe external database schema information:\n"
        context_prompt += repr(self.context_manager.inspect_external_database())

        return context_prompt

    def get_dataframe_schema_and_sample_values(self) -> str:
        """
        Describe the structure and sample values of the working dataset.

        The method inspects the dataset loaded into the analytical environment
        and summarizes column types along with representative values to guide
        analytical reasoning.
        """
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

    def get_last_saved_sql_query(self, state: State) -> str:
        """
        Retrieve the most recently persisted SQL query.

        This information provides historical context for analytical continuity,
        especially when subsequent reasoning depends on prior data extraction.
        """
        if sql_query := self.memory_manager.show_last_saved_sql_query():
            context_prompt: str = "\n\nThe dataframe representation above is previously extracted from external database using the following SQL query:\n"
            context_prompt += str(sql_query)

            return context_prompt

        return "\n\nThere is no SQL query executed previously."

    def get_data_unavailability_rationale(self, state: State) -> str:
        """
        Explain why required analytical data is unavailable.

        This rationale is produced during analysis orchestration and is used
        to justify alternative response paths when data constraints exist.
        """
        if state["analysis_orchestration"]:
            context_prompt: str = "\n\nThe rationale of why required data does not exist in external database:"
            context_prompt += f"\n{state["analysis_orchestration"].rationale}"

            return context_prompt

        raise ValueError(f"'analysis_orchestration' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_last_executed_sql_query(self, state: State) -> str:
        """
        Provide the SQL query used in the most recent data extraction.

        This context links analytical results back to their data provenance.
        """
        if state["analysis_orchestration"]:
            context_prompt: str = "\n\nThe dataframe representation above is previously extracted from external database using the following SQL query:\n"
            context_prompt += str(state["analysis_orchestration"].sql_query)
            context_prompt += f"\nThe rationale of executed SQL query: {state["analysis_orchestration"].syntax_rationale}"

            return context_prompt

        raise ValueError(f"'analysis_orchestration' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_python_code(self, state: State, runtime: Runtime[Context]) -> str:
        """
        Generate the executable Python code for sandbox execution.

        This method assembles the sandbox bootstrap code based on the analysis type.
        """
        code: str = ""

        if state["computation_planning"]:
            code += runtime.context.sandbox_bootstrap[state["computation_planning"].analysis_type]

            for step in state["computation_planning"].steps:
                code += '\n' + step.python_code + '\n'

            return code
        else:
            raise ValueError(f"'computation_planning' state must not be empty in '{sys._getframe(0).f_code.co_name}' node")

    def get_computational_plan(self, state: State, original: bool = False) -> str:
        """
        List the analytical computation steps that were generated.

        The output represents the structured plan used to guide sandbox
        execution and subsequent observation.
        """
        if state["computation_planning"]:
            context_prompt: str = "\n\nThe step-by-step computational plan:"

            for step in state["computation_planning"].steps:
                context_prompt += f"\n{step.number}. {step.description} {step}" if not original else f"\n- {step}"

            return context_prompt

        raise ValueError(f"'computation_planning' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_execution_stdout(self, state: State) -> str:
        """
        Retrieve standard output produced by sandbox execution.

        This information reflects the observable results of analytical
        computations and is used during result evaluation.
        """
        if state["execution"]:
            context_prompt: str = "\n\nThe execution logs from the sandbox environment:\n"
            context_prompt += str(state["execution"].logs.stdout[0])

            return context_prompt

        raise ValueError(f"'execution' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_execution_error(self, state: State) -> str:
        """
        Retrieve execution error details from the sandbox environment.

        The returned traceback supports error diagnosis and corrective
        planning during self-correction stages.
        """
        if state["execution"] and state["execution"].error:
            context_prompt: str = "\n\nThe traceback error messages from sandbox environment:\n"
            context_prompt += state["execution"].error.traceback

            return context_prompt

        raise ValueError(f"'execution' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_observation_rationale(self, state: State) -> str:
        """
        Retrieve the rationale produced during result observation.

        This explanation is used to determine whether analytical outcomes
        are sufficient or require further refinement.
        """
        if state["observation"]:
            context_prompt: str = "\n\nThe observation result on executed computational plan:\n"
            context_prompt += state["observation"].rationale

            return context_prompt

        raise ValueError(f"'observation' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")
