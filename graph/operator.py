
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
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from pandas.errors import EmptyDataError

# internal
from .state import State
from context.database import DatabaseManager
from context.datasets import working_dataset_path
from context.models import (
    ChatHistory,
    ChatHistoryShow,
    ShortMemory
)

class Operator:
    """
    Docstring for ContextManager
    """
    def __init__(self, database_manager: DatabaseManager) -> None:
        """
        Docstring for __init__
        
        :param self: Description
        """
        self.database_manager: DatabaseManager = database_manager

    def get_conversation_summary(self) -> str:
        """
        Docstring for get_conversation_summary
        
        :param self: Description
        :param database_manager: Description
        :type database_manager: DatabaseManager
        :return: Description
        :rtype: str
        """
        short_memories: List[ShortMemory] = self.database_manager.index_short_memory()

        if short_memories:
            context_prompt: str = "\n\nConversation history summarized by turn number:"

            for short_memory in short_memories:
                context_prompt += f"\nTurn-{short_memory.turn_num}: {short_memory.summary}"

            return context_prompt

        return "\n\nThere is no conversation history."

    def get_relevant_conversation(self, state: State) -> Sequence:
        """
        Docstring for relevant_chat_turn
        
        :param self: Description
        :param state: Description
        :type state: State
        :param database_manager: Description
        :type database_manager: DatabaseManager
        :return: Description
        :rtype: Sequence[Any]
        """
        llm_input: Sequence = []

        if state["intent_comprehension"]:
            for turn_num in state["intent_comprehension"].relevant_turns:
                params: ChatHistoryShow = ChatHistoryShow(turn_num=int(turn_num))
                relevant_turn: List[ChatHistory] = self.database_manager.show_chat_history(params)

                for chat in relevant_turn:
                    if chat.role == "Human":
                        llm_input += [HumanMessage(content=chat.content)]
                    else:
                        llm_input += [AIMessage(content=chat.content)]

        return llm_input

    def get_database_schema_and_sample_values(self) -> str:
        """
        Docstring for get_database_schema_and_sample_values
        
        :param self: Description
        :param database_manager: Description
        :type database_manager: DatabaseManager
        :return: Description
        :rtype: str
        """
        context_prompt: str = "\n\nExternal database schema information:\n"
        context_prompt += repr(self.database_manager.inspect_external_database())

        return context_prompt

    def get_dataframe_schema_and_sample_values(self) -> str:
        """
        Docstring for get_dataframe_schema_and_sample_values
        
        :param self: Description
        :return: Description
        :rtype: str
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
        Docstring for get_last_saved_sql_query
        
        :param self: Description
        :param state: Description
        :type state: State
        :param database_manager: Description
        :type database_manager: DatabaseManager
        :return: Description
        :rtype: str
        """
        if sql_query := self.database_manager.show_last_saved_sql_query():
            context_prompt: str = "\n\nThe dataframe object representation above is extracted using the following SQL query:\n"
            context_prompt += str(sql_query)

            return context_prompt

        return "\n\nThere is no SQL query executed previously."

    def get_data_unavailability_rationale(self, state: State) -> str:
        """
        Docstring for get_data_unavailability_rationale
        
        :param self: Description
        :param state: Description
        :type state: State
        :return: Description
        :rtype: str
        """
        if state["analysis_orchestration"]:
            context_prompt: str = "\n\nThe rationale of why required data does not exist in external database:"
            context_prompt += f"\n{state["analysis_orchestration"].rationale}"

            return context_prompt

        raise ValueError(f"'analysis_orchestration' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_last_executed_sql_query(self, state: State) -> str:
        """
        Docstring for get_last_executed_sql_query
        
        :param self: Description
        :param state: Description
        :type state: State
        :return: Description
        :rtype: str
        """
        if state["analysis_orchestration"]:
            context_prompt: str = "\n\nThe dataframe object representation above is extracted using the following SQL query:\n"
            context_prompt += str(state["analysis_orchestration"].sql_query)

            return context_prompt

        raise ValueError(f"'analysis_orchestration' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_computational_plan_list(self, state: State) -> str:
        """
        Docstring for get_computational_plan_list
        
        :param self: Description
        :param state: Description
        :type state: State
        :return: Description
        :rtype: str
        """
        if state["computation_planning"]:
            context_prompt: str = "\n\nThe computation plan that was generated:"

            for step in state["computation_planning"].steps:
                context_prompt += f"\n- {step}"

            return context_prompt

        raise ValueError(f"'computation_planning' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_execution_stdout(self, state: State) -> str:
        """
        Docstring for get_execution_stdout
        
        :param self: Description
        :param state: Description
        :type state: State
        :return: Description
        :rtype: str
        """
        if state["execution"]:
            context_prompt: str = "\n\nThe execution logs from sandbox environment:\n"
            context_prompt += str(state["execution"].logs.stdout[0])

            return context_prompt

        raise ValueError(f"'execution' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_execution_error(self, state: State) -> str:
        """
        Docstring for get_execution_error
        
        :param self: Description
        :param state: Description
        :type state: State
        :return: Description
        :rtype: str
        """
        if state["execution"] and state["execution"].error:
            context_prompt: str = "\n\nThe traceback error:\n"
            context_prompt += state["execution"].error.traceback

            return context_prompt

        raise ValueError(f"'execution' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_observation_rationale(self, state: State) -> str:
        """
        Docstring for get_observation_rationale
        
        :param self: Description
        :param state: Description
        :type state: State
        :return: Description
        :rtype: str
        """
        if state["observation"]:
            context_prompt: str = "\n\nThe observation rationale:\n"
            context_prompt += state["observation"].rationale

            return context_prompt

        raise ValueError(f"'observation' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")
