"""
Docstring for graph.orchestrator
"""
# standard
import sys
from typing import (
    Any,
    Dict,
    Literal,
    Sequence,
)

# third-party
from e2b_code_interpreter import Execution
from e2b_code_interpreter.code_interpreter_sync import Sandbox
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
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

# internal
from .operator import Operator
from .runtime import Context
from .state import State
from context.database import DatabaseManager
from context.datasets import working_dataset_path
from context.models import (
    ChatHistoryCreate,
    ShortMemoryCreate
)
from schema import (
    AnalysisOrchestration,
    ComputationPlanning,
    IntentComprehension,
    Observation,
    RequestClassification,
)

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
        self.operator: Operator = Operator(self.database_manager)

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
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = "\n\nContext information is provided below."
        context_prompt += self.operator.get_conversation_summary()
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message] + state["messages"]

        llm: Runnable = self.gpt_120b.with_structured_output(
            schema=IntentComprehension,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: IntentComprehension = IntentComprehension.model_validate(llm_output)

        return {
            "ui_payload": "Classifying request",
            "intent_comprehension": serialized_output,
        }

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
        llm_input += self.operator.get_relevant_conversation(state)
        llm_input += state["messages"]

        llm: Runnable = self.gpt_120b.with_structured_output(
            schema=RequestClassification,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: RequestClassification = RequestClassification.model_validate(llm_output)

        match serialized_output.route:
            case "analysis_orchestration":
                return Command(
                    goto="analysis_orchestration",
                    update={
                        "ui_payload": "Determining strategy for analysis",
                        "request_classification": serialized_output
                    }
                )
            case "direct_response":
                return Command(
                    goto="direct_response",
                    update={
                        "ui_payload": "Formulating response without analytical computation",
                        "request_classification": serialized_output
                    }
                )
            case "punt_response":
                return Command(
                    goto="punt_response",
                    update={
                        "ui_payload": "Formulating response that request is out of business analytical domain",
                        "request_classification": serialized_output
                    }
                )
            case _:
                raise ValueError("Unknown route category")

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
        llm_input += self.operator.get_relevant_conversation(state)
        llm_input += state["messages"]
        llm_output: AIMessage = self.gpt_120b.invoke(llm_input)

        return {
            "ui_payload": "Finalizing response",
            "messages": [llm_output]
        }

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

        return {
            "ui_payload": "Finalizing response",
            "messages": [llm_output]
        }

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
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = "\n\nContext information is provided below."
        context_prompt += self.operator.get_database_schema_and_sample_values()
        context_prompt += self.operator.get_dataframe_schema_and_sample_values()
        context_prompt += self.operator.get_last_saved_sql_query(state)
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]
        llm_input += self.operator.get_relevant_conversation(state)
        llm_input += state["messages"]

        llm: Runnable = self.gpt_120b.with_structured_output(
            schema=AnalysisOrchestration,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: AnalysisOrchestration = AnalysisOrchestration.model_validate(llm_output)

        match serialized_output.route:
            case "data_unavailability":
                return Command(
                    goto="data_unavailability",
                    update={
                        "ui_payload": "Discovering that business data is insufficient to perform analytical computation",
                        "analysis_orchestration": serialized_output
                    }
                )
            case "data_retrieval":
                return Command(
                    goto="data_retrieval",
                    update={
                        "ui_payload": "Extracting business data from external database",
                        "analysis_orchestration": serialized_output
                    }
                )
            case "computation_planning":
                return Command(
                    goto="computation_planning",
                    update={
                        "ui_payload": "Creating analytical computation plan",
                        "analysis_orchestration": serialized_output
                    }
                )
            case _:
                raise ValueError("Unknown route category")

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
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = "\n\nContext information is provided below."
        context_prompt += self.operator.get_data_unavailability_rationale(state)
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]
        llm_input += self.operator.get_relevant_conversation(state)
        llm_input += state["messages"]
        llm_output: AIMessage = self.gpt_120b.invoke(llm_input)

        return {
            "ui_payload": "Finalizing response",
            "messages": [llm_output]
        }

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
                self.database_manager.extract_external_database(sql_query)

                return {"ui_payload": "Creating analytical computation plan"}

            raise ValueError("'analysis_orchestration' state does not contains 'sql_query' attribute when retrieving data")
        else:
            raise ValueError("'analysis_orchestration' state must not empty in 'data_retrieval' node")

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
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = "\n\nContext information is provided below."
        context_prompt += self.operator.get_dataframe_schema_and_sample_values()
        context_prompt += self.operator.get_last_executed_sql_query(state)
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]
        llm_input += self.operator.get_relevant_conversation(state)
        llm_input += state["messages"]

        llm: Runnable = self.gpt_120b.with_structured_output(
            schema=ComputationPlanning,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: ComputationPlanning = ComputationPlanning.model_validate(llm_output)

        return {
            "ui_payload": "Executing analytical computation plan",
            "computation_planning": serialized_output
        }

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

        with open(working_dataset_path, "rb") as dataset:
            sandbox.files.write('dataset.csv', dataset.read())

        code : str = runtime.context.sandbox_bootstrap

        if state["computation_planning"]:
            for step in state["computation_planning"].steps:
                code += step.python_code + '\n'
        else:
            raise ValueError("'computation_planning' state must not be empty in 'sandbox_environment' node")

        execution: Execution = sandbox.run_code(code)
        sandbox.kill()

        match execution.error is None:
            case True:
                return Command(
                    goto="observation",
                    update={
                        "ui_payload": "Observing computational execution result",
                        "execution": execution
                    }
                )
            case False:
                return Command(
                    goto="self_correction",
                    update={
                        "ui_payload": "Correcting analytical computation syntax",
                        "execution": execution
                    }
                )

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
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = "\n\nContext information is provided below."
        context_prompt += self.operator.get_dataframe_schema_and_sample_values()
        context_prompt += self.operator.get_last_executed_sql_query(state)
        context_prompt += self.operator.get_computational_plan_list(state)
        context_prompt += self.operator.get_execution_stdout(state)
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]
        llm_input += self.operator.get_relevant_conversation(state)
        llm_input += state["messages"]

        llm: Runnable = self.gpt_120b.with_structured_output(
            schema=Observation,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: Observation = Observation.model_validate(llm_output)

        match serialized_output.status:
            case "insufficient":
                return Command(
                    goto="self_reflection",
                    update={
                        "ui_payload": "Reflecting analytical plan for better analytical result",
                        "observation": serialized_output
                    }
                )
            case "sufficient":
                return Command(
                    goto="analysis_response",
                    update={
                        "ui_payload": "Formulating response based on observation result",
                        "observation": serialized_output
                    }
                )
            case _:
                raise ValueError("Unknown status value")

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
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = "\n\nContext information is provided below."
        context_prompt += self.operator.get_computational_plan_list(state)
        context_prompt += self.operator.get_execution_error(state)
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]

        llm: Runnable = self.gpt_120b.with_structured_output(
            schema=ComputationPlanning,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: ComputationPlanning = ComputationPlanning.model_validate(llm_output)

        return {
            "ui_payload": "Executing analytical computation plan with corrected syntax",
            "computation_planning": serialized_output
        }

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
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = "\n\nContext information is provided below."
        context_prompt += self.operator.get_computational_plan_list(state)
        context_prompt += self.operator.get_observation_rationale(state)
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]

        llm: Runnable = self.gpt_120b.with_structured_output(
            schema=ComputationPlanning,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: ComputationPlanning = ComputationPlanning.model_validate(llm_output)

        return {
            "ui_payload": "Executing refined analytical computation plan",
            "computation_planning": serialized_output
        }

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
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = "\n\nContext information is provided below."
        context_prompt += self.operator.get_database_schema_and_sample_values()
        context_prompt += self.operator.get_dataframe_schema_and_sample_values()
        context_prompt += self.operator.get_last_executed_sql_query(state)
        context_prompt += self.operator.get_computational_plan_list(state)
        context_prompt += self.operator.get_execution_stdout(state)
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]
        llm_input += self.operator.get_relevant_conversation(state)
        llm_input += state["messages"]
        llm_output: AIMessage = self.gpt_120b.invoke(llm_input)

        return {
            "ui_payload": "Finalizing response",
            "messages": [llm_output]
        }

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
