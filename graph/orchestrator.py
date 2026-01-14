"""
Docstring for graph.orchestrator
"""
# standard
import sys
from io import StringIO
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Sequence,
)

# third-party
import pandas as pd
import streamlit as st
from e2b_code_interpreter import Execution
from e2b_code_interpreter.code_interpreter_sync import Sandbox
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain_core.runnables import Runnable
from langchain_groq import ChatGroq
from langgraph.graph import (
    StateGraph,
    END,
    START,
)
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime
from langgraph.types import Command
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

# internal
from .runtime import Context
from .state import State
from context.database import DatabaseManager
from context.models import (
    ChatHistory,
    ChatHistoryCreate,
    ChatHistoryShow,
    ShortMemoryCreate
)
from schema import (
    AnalysisOrchestration,
    ComputationPlanning,
    IntentComprehension,
    Observation,
    RequestClassification,
)
from util import st_status_container

class Orchestrator:
    """
    Docstring for Orchestrator
    
    :var Returns: Description
    """
    def __init__(self) -> None:
        """
        Docstring for __init__
        
        :param self: Description
        """
        self.database_manager: DatabaseManager = DatabaseManager()

        self.gpt_120b: BaseChatModel = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0,
            max_tokens=None,
            reasoning_format="parsed",
            reasoning_effort="high",
        )

        self.graph_builder: StateGraph[State, Context] = StateGraph(
            state_schema=State,
            context_schema=Context,
        )

    @st_status_container("Understanding request intent")
    def intent_comprehension(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """
        Docstring for intent_comprehension
        
        :param self: Description
        :param state: Description
        :type state: State
        :param runtime: Description
        :type runtime: Runtime[Context]
        :return: Description
        :rtype: Dict[str, Any]
        """
        context_prompt: str = "\n\nContext information is provided below."

        if runtime.context.short_memories:
            context_prompt += "\n\nConversation history summarized by turn number:"

            for num, turn in enumerate(runtime.context.short_memories):
                context_prompt += f"\n{num + 1}. {turn.summary}"
        else:
            context_prompt += "\n\nThere is no conversation history."

        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message] + state["messages"]

        llm: Runnable = self.gpt_120b.with_structured_output(
            schema=IntentComprehension,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: IntentComprehension = IntentComprehension.model_validate(llm_output)

        return {"intent_comprehension": serialized_output}

    @st_status_container("Classifying request")
    def request_classification(self, state: State, runtime: Runtime[Context]) -> Command[Literal["analysis_orchestration", "direct_response", "punt_response"]]:
        """
        Docstring for request_classification
        
        :param self: Description
        :param state: Description
        :type state: State
        :param runtime: Description
        :type runtime: Runtime[Context]
        :return: Description
        :rtype: Command[Literal['analysis_orchestration', 'direct_response', 'punt_response']]
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt)
        llm_input: Sequence = [system_message]

        if state["intent_comprehension"]:
            for turn in state["intent_comprehension"].relevant_turns:
                params: ChatHistoryShow = ChatHistoryShow(turn_num=turn)
                relevant_turn: List[ChatHistory] = self.database_manager.show_chat_history(params)

                for chat in relevant_turn:
                    if chat.role == "Human":
                        llm_input += [HumanMessage(content=chat.content)]
                    else:
                        llm_input += [AIMessage(content=chat.content)]

        llm_input += state["messages"]

        llm: Runnable = self.gpt_120b.with_structured_output(
            schema=RequestClassification,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: RequestClassification = RequestClassification.model_validate(llm_output)
        return_state: Dict[Literal["request_classification"], RequestClassification] = {"request_classification": serialized_output}

        match serialized_output.route:
            case "analysis_orchestration":
                return Command(
                    goto="analysis_orchestration",
                    update=return_state
                )
            case "direct_response":
                return Command(
                    goto="direct_response",
                    update=return_state
                )
            case "punt_response":
                return Command(
                    goto="punt_response",
                    update=return_state
                )
            case _:
                raise ValueError("Unknown route category")

    @st_status_container("Formulating response without analytical computation")
    def direct_response(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """
        Docstring for direct_response
        
        :param self: Description
        :param state: Description
        :type state: State
        :param runtime: Description
        :type runtime: Runtime[Context]
        :return: Description
        :rtype: Dict[str, Any]
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt)
        llm_input: Sequence = [system_message]

        if state["intent_comprehension"]:
            for turn in state["intent_comprehension"].relevant_turns:
                params: ChatHistoryShow = ChatHistoryShow(turn_num=turn)
                relevant_turn: List[ChatHistory] = self.database_manager.show_chat_history(params)

                for chat in relevant_turn:
                    if chat.role == "Human":
                        llm_input += [HumanMessage(content=chat.content)]
                    else:
                        llm_input += [AIMessage(content=chat.content)]

        llm_input += state["messages"]
        llm_output: AIMessage = self.gpt_120b.invoke(llm_input)

        return {"messages": [llm_output]}

    @st_status_container("Formulating response that request is outside business analytics domain")
    def punt_response(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """
        Docstring for punt_response
        
        :param self: Description
        :param state: Description
        :type state: State
        :param runtime: Description
        :type runtime: Runtime[Context]
        :return: Description
        :rtype: Dict[str, Any]
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt)
        llm_input: Sequence = [system_message] + state["messages"]
        llm_output: AIMessage = self.gpt_120b.invoke(llm_input)

        return {"messages": [llm_output]}

    @st_status_container("Determining analysis strategy")
    def analysis_orchestration(self, state: State, runtime: Runtime[Context]) -> Command[Literal["data_unavailability", "data_retrieval", "computation_planning"]]:
        """
        Docstring for analysis_orchestration
        
        :param self: Description
        :param state: Description
        :type state: State
        :param runtime: Description
        :type runtime: Runtime[Context]
        :return: Description
        :rtype: Command[Literal['data_unavailability', 'data_retrieval', 'computation_planning']]
        """
        context_prompt: str = "\n\nContext information is provided below."
        context_prompt += "\n\nExternal database schema information:\n"
        context_prompt += repr(runtime.context.external_db_info)

        if state["dataframe"] is not None:
            buffer: StringIO = StringIO()
            state["dataframe"].info(buf=buffer, memory_usage=False)
            context_prompt += "\n\nDataframe object representation:\n"
            context_prompt += buffer.getvalue()
            context_prompt += "\n\nDataframe object is extracted previously using the following SQL query:\n"
            context_prompt += str(self.database_manager.get_last_executed_sql_query())
        else:
            context_prompt += "\n\nThere is no dataframe object representation."

        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]

        if state["intent_comprehension"]:
            for turn in state["intent_comprehension"].relevant_turns:
                params: ChatHistoryShow = ChatHistoryShow(turn_num=turn)
                relevant_turn: List[ChatHistory] = self.database_manager.show_chat_history(params)

                for chat in relevant_turn:
                    if chat.role == "Human":
                        llm_input += [HumanMessage(content=chat.content)]
                    else:
                        llm_input += [AIMessage(content=chat.content)]

        llm_input += state["messages"]

        llm: Runnable = self.gpt_120b.with_structured_output(
            schema=AnalysisOrchestration,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: AnalysisOrchestration = AnalysisOrchestration.model_validate(llm_output)
        return_state: Dict[Literal["analysis_orchestration"], AnalysisOrchestration] = {"analysis_orchestration": serialized_output}

        match serialized_output.route:
            case "data_unavailability":
                return Command(
                    goto="data_unavailability",
                    update=return_state
                )
            case "data_retrieval":
                return Command(
                    goto="data_retrieval",
                    update=return_state
                )
            case "computation_planning":
                return Command(
                    goto="computation_planning",
                    update=return_state
                )
            case _:
                raise ValueError("Unknown route category")

    @st_status_container("Discovering that business data is unavailable to complete request")
    def data_unavailability(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """
        Docstring for data_unavailability
        
        :param self: Description
        :param state: Description
        :type state: State
        :param runtime: Description
        :type runtime: Runtime[Context]
        :return: Description
        :rtype: Dict[str, Any]
        """
        context_prompt: str = "\n\nContext information is provided below."

        if state["analysis_orchestration"]:
            context_prompt += f"\n\n{state["analysis_orchestration"].rationale}"

        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]

        if state["intent_comprehension"]:
            for turn in state["intent_comprehension"].relevant_turns:
                params: ChatHistoryShow = ChatHistoryShow(turn_num=turn)
                relevant_turn: List[ChatHistory] = self.database_manager.show_chat_history(params)

                for chat in relevant_turn:
                    if chat.role == "Human":
                        llm_input += [HumanMessage(content=chat.content)]
                    else:
                        llm_input += [AIMessage(content=chat.content)]

        llm_input += state["messages"]
        llm_output: AIMessage = self.gpt_120b.invoke(llm_input)

        return {"messages": llm_output}

    @st_status_container("Extracting business data from external database")
    def data_retrieval(self, state: State) -> Dict[str, Any]:
        """
        Docstring for data_retrieval
        
        :param self: Description
        :param state: Description
        :type state: State
        :return: Description
        :rtype: Dict[str, Any]
        """
        if state["analysis_orchestration"]:
            if state["analysis_orchestration"].sql_query:
                sql_query: str = state["analysis_orchestration"].sql_query
                self.database_manager.retrieve_external_data(sql_query)

                return {"dataframe": self.database_manager.get_working_dataframe()}

            raise ValueError("'analysis_orchestration' state does not contains 'sql_query' attribute when retrieving data")
        else:
            raise ValueError("'analysis_orchestration' state must not empty in 'data_retrieval' node")

    @st_status_container("Planning computation steps on data")
    def computation_planning(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """
        Docstring for computation_planning
        
        :param self: Description
        :param state: Description
        :type state: State
        :param runtime: Description
        :type runtime: Runtime[Context]
        :return: Description
        :rtype: Dict[str, Any]
        """
        context_prompt: str = "\n\nContext information is provided below."

        if state["dataframe"] is not None and state["analysis_orchestration"] is not None:
            context_prompt += "\n\nDataframe schema and sample values in each columns:"
            col_value_dict: Dict[str, tuple[str, Any]] = {}
            dset_attrs: str = ""
            df: pd.DataFrame = state["dataframe"]

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
        else:
            raise ValueError("'dataframe' state must not be empty in 'computation_planning' node")

        if state["analysis_orchestration"]:
            context_prompt += "\n\nThe dataframe object representation above is extracted using the following SQL query:\n"
            context_prompt += str(state["analysis_orchestration"].sql_query)
        else:
            raise ValueError("'analysis_orchestration' state must not be empty in 'observation' node")

        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]

        if state["intent_comprehension"]:
            for turn in state["intent_comprehension"].relevant_turns:
                params: ChatHistoryShow = ChatHistoryShow(turn_num=turn)
                relevant_turn: List[ChatHistory] = self.database_manager.show_chat_history(params)

                for chat in relevant_turn:
                    if chat.role == "Human":
                        llm_input += [HumanMessage(content=chat.content)]
                    else:
                        llm_input += [AIMessage(content=chat.content)]

        llm_input += state["messages"]

        llm: Runnable = self.gpt_120b.with_structured_output(
            schema=ComputationPlanning,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: ComputationPlanning = ComputationPlanning.model_validate(llm_output)

        return {"computation_planning": serialized_output}

    @st_status_container("Executing plan")
    def sandbox_environment(self, state: State, runtime: Runtime[Context]) -> Command[Literal["observation", "self_correction"]]:
        """
        Docstring for sandbox_environment
        
        :param self: Description
        :param state: Description
        :type state: State
        :param runtime: Description
        :type runtime: Runtime[Context]
        :return: Description
        :rtype: Command[Literal['observation', 'self_correction']]
        """
        sandbox: Sandbox = Sandbox.create()

        with open("./context/working_dataset.csv", "rb") as dataset:
            sandbox.files.write('dataset.csv', dataset.read())

        code : str = runtime.context.sandbox_bootstrap

        if state["computation_planning"]:
            for step in state["computation_planning"].steps:
                code += step.python_code + '\n'
        else:
            raise ValueError("'computation_planning' state must not be empty in 'sandbox_environment' node")

        execution: Execution = sandbox.run_code(code)
        sandbox.kill()
        return_state: Dict[Literal["execution"], Execution] = {"execution": execution}

        match execution.error is None:
            case True:
                return Command(
                    goto="observation",
                    update=return_state
                )
            case False:
                st.error("There's computational execution error")

                return Command(
                    goto="self_correction",
                    update=return_state
                )

    @st_status_container("Observing execution result")
    def observation(self, state: State, runtime: Runtime[Context]) -> Command[Literal["self_reflection", "analysis_response"]]:
        """
        Docstring for observation
        
        :param self: Description
        :param state: Description
        :type state: State
        :param runtime: Description
        :type runtime: Runtime[Context]
        :return: Description
        :rtype: Command[Literal['self_reflection', 'analysis_response']]
        """
        context_prompt: str = "\n\nContext information is provided below."

        if state["dataframe"] is not None:
            context_prompt += "\n\nDataframe schema and sample values in each columns:"
            col_value_dict: Dict[str, tuple[str, Any]] = {}
            dset_attrs: str = ""
            df: pd.DataFrame = state["dataframe"]

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
        else:
            raise ValueError("'dataframe' state must not be empty in 'observation' node")

        if state["analysis_orchestration"]:
            context_prompt += "\n\nThe dataframe object representation above is extracted using the following SQL query:\n"
            context_prompt += str(state["analysis_orchestration"].sql_query)
        else:
            raise ValueError("'analysis_orchestration' state must not be empty in 'observation' node")

        if state["computation_planning"]:
            context_prompt += "\n\nThe computation plan that was generated:"

            for step in state["computation_planning"].steps:
                context_prompt += f"\n{step.number}. {step.description}"
        else:
            raise ValueError("'computation_planning' state must not be empty in 'observation' node")

        if state["execution"]:
            context_prompt += "\n\nThe execution logs from sandbox environment:\n"
            context_prompt += str(state["execution"].logs.stdout)
        else:
            raise ValueError("'execution' state must not be empty in 'observation' node")

        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]

        if state["intent_comprehension"]:
            for turn in state["intent_comprehension"].relevant_turns:
                params: ChatHistoryShow = ChatHistoryShow(turn_num=turn)
                relevant_turn: List[ChatHistory] = self.database_manager.show_chat_history(params)

                for chat in relevant_turn:
                    if chat.role == "Human":
                        llm_input += [HumanMessage(content=chat.content)]
                    else:
                        llm_input += [AIMessage(content=chat.content)]

        llm_input += state["messages"]

        llm: Runnable = self.gpt_120b.with_structured_output(
            schema=Observation,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: Observation = Observation.model_validate(llm_output)
        return_state: Dict[Literal["observation"], Observation] = {"observation": serialized_output}

        match serialized_output.status:
            case "insufficient":
                return Command(
                    goto="self_reflection",
                    update=return_state
                )
            case "sufficient":
                return Command(
                    goto="analysis_response",
                    update=return_state
                )
            case _:
                raise ValueError("Unknown status value")

    @st_status_container("Correcting computational syntax")
    def self_correction(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """
        Docstring for self_correction
        
        :param self: Description
        :param state: Description
        :type state: State
        :param runtime: Description
        :type runtime: Runtime[Context]
        :return: Description
        :rtype: Dict[str, Any]
        """
        context_prompt: str = "\n\nContext information is provided below."

        if state["computation_planning"]:
            context_prompt += "\n\nThe original computational plan:"

            for step in state["computation_planning"].steps:
                context_prompt += f"\n{step}"
        else:
            raise ValueError("'computation_planning' state must not be empty in 'self_correction' node")

        if state["execution"] and state["execution"].error:
            context_prompt += "\n\nThe traceback error:\n"
            context_prompt += state["execution"].error.traceback
        else:
            raise ValueError("'execution' state must not be empty in 'self_correction' node")

        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]

        llm: Runnable = self.gpt_120b.with_structured_output(
            schema=ComputationPlanning,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: ComputationPlanning = ComputationPlanning.model_validate(llm_output)

        return {"computation_planning": serialized_output}

    @st_status_container("Reflecting computational plan for better results")
    def self_reflection(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """
        Docstring for self_reflection
        
        :param self: Description
        :param state: Description
        :type state: State
        :param runtime: Description
        :type runtime: Runtime[Context]
        :return: Description
        :rtype: Dict[str, Any]
        """
        context_prompt: str = "\n\nContext information is provided below."

        if state["computation_planning"]:
            context_prompt += "\n\nThe original computational plan:"

            for step in state["computation_planning"].steps:
                context_prompt += f"\n{step}"
        else:
            raise ValueError("'computation_planning' state must not be empty in 'self_reflection' node")

        if state["observation"]:
            context_prompt += "\n\nThe observation rationale:\n"
            context_prompt += state["observation"].rationale
        else:
            raise ValueError("'observation' state must not be empty in 'self_reflection' node")

        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]

        llm: Runnable = self.gpt_120b.with_structured_output(
            schema=ComputationPlanning,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: ComputationPlanning = ComputationPlanning.model_validate(llm_output)

        return {"computation_planning": serialized_output}

    @st_status_container("Formulating response for analysis result")
    def analysis_response(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """
        Docstring for analysis_response
        
        :param self: Description
        :param state: Description
        :type state: State
        :param runtime: Description
        :type runtime: Runtime[Context]
        :return: Description
        :rtype: Dict[str, Any]
        """
        context_prompt: str = "\n\nContext information is provided below."

        if state["computation_planning"]:
            context_prompt += "\n\nThe final computational plan:"

            for step in state["computation_planning"].steps:
                context_prompt += f"\n{step}"
        else:
            raise ValueError("'computation_planning' state must not be empty in 'self_reflection' node")

        if state["execution"]:
            context_prompt += "\n\nThe execution logs from sandbox environment:\n"
            context_prompt += str(state["execution"].logs.stdout)
        else:
            raise ValueError("'execution' state must not be empty in 'analysis_response' node")

        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]

        if state["intent_comprehension"]:
            for turn in state["intent_comprehension"].relevant_turns:
                params: ChatHistoryShow = ChatHistoryShow(turn_num=turn)
                relevant_turn: List[ChatHistory] = self.database_manager.show_chat_history(params)

                for chat in relevant_turn:
                    if chat.role == "Human":
                        llm_input += [HumanMessage(content=chat.content)]
                    else:
                        llm_input += [AIMessage(content=chat.content)]

        llm_input += state["messages"]
        llm_output: AIMessage = self.gpt_120b.invoke(llm_input)

        return {"messages": [llm_output]}

    @st_status_container("Finalizing response")
    def summarization(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """
        Docstring for summarization
        
        :param self: Description
        :param state: Description
        :type state: State
        :param runtime: Description
        :type runtime: Runtime[Context]
        :return: Description
        :rtype: Dict[str, Any]
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt)
        llm_input: Sequence = [system_message] + state["messages"]
        llm_output: AIMessage = self.gpt_120b.invoke(llm_input)

        turn_num = runtime.context.turn_num + 1

        create_chat_history_params: ChatHistoryCreate = ChatHistoryCreate(
            turn_num=turn_num,
            role="Human",
            content=str(state["messages"][0].content)
        )

        self.database_manager.store_chat_history(create_chat_history_params())

        create_chat_history_params = ChatHistoryCreate(
            turn_num=turn_num,
            role="AI",
            content=str(state["messages"][1].content)
        )

        self.database_manager.store_chat_history(create_chat_history_params())

        create_short_memory_params: ShortMemoryCreate = ShortMemoryCreate(
            turn_num=turn_num,
            summary=str(llm_output.content),
            sql_query=state["analysis_orchestration"].sql_query if state["analysis_orchestration"] else None
        )

        self.database_manager.store_short_memory(create_short_memory_params())

        return {"summarization": llm_output}

    def build_graph(self) -> CompiledStateGraph[State, Context]:
        """
        Docstring for build_graph
        
        :param self: Description
        :return: Description
        :rtype: CompiledStateGraph[State, Context, State, State]
        """
        self.graph_builder.add_node("intent_comprehension", self.intent_comprehension)
        self.graph_builder.add_node("request_classification", self.request_classification)
        self.graph_builder.add_node("direct_response", self.direct_response)
        self.graph_builder.add_node("punt_response", self.punt_response)
        self.graph_builder.add_node("analysis_orchestration", self.analysis_orchestration)
        self.graph_builder.add_node("data_unavailability", self.data_unavailability)
        self.graph_builder.add_node("data_retrieval", self.data_retrieval)
        self.graph_builder.add_node("computation_planning", self.computation_planning)
        self.graph_builder.add_node("sandbox_environment", self.sandbox_environment)
        self.graph_builder.add_node("observation", self.observation)
        self.graph_builder.add_node("self_correction", self.self_correction)
        self.graph_builder.add_node("self_reflection", self.self_reflection)
        self.graph_builder.add_node("analysis_response", self.analysis_response)
        self.graph_builder.add_node("summarization", self.summarization)

        self.graph_builder.add_edge(START, "intent_comprehension")
        self.graph_builder.add_edge("intent_comprehension", "request_classification")
        self.graph_builder.add_edge("data_retrieval", "computation_planning")
        self.graph_builder.add_edge("computation_planning", "sandbox_environment")
        self.graph_builder.add_edge("self_correction", "sandbox_environment")
        self.graph_builder.add_edge("self_reflection", "sandbox_environment")
        self.graph_builder.add_edge("analysis_response", "summarization")
        self.graph_builder.add_edge("direct_response", "summarization")
        self.graph_builder.add_edge("data_unavailability", "summarization")
        self.graph_builder.add_edge("summarization", END)
        self.graph_builder.add_edge("punt_response", END)

        return self.graph_builder.compile()
