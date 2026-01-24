"""
Execution coordination layer for the graph-based workflow.

This module defines graph nodes and edges that orchestrate analytical
process. Each public method represents a LangGraph node responsible for 
certain responsibility that accomplishes agentic workflow altogether.
"""
# standard
import sys
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Sequence,
    Union,
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
from langgraph.graph import (
    StateGraph,
    END,
    START,
)
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime
from langgraph.types import Command

# internal
from .composer import Composer
from .runtime import Context
from .state import State
from context.database import ContextManager
from language_model.schema import (
    IntentComprehension,
    RequestClassification,
    AnalyticalRequirement,
    DataAvailability,
    DataRetrievalPlanning,
    DataRetrievalObservation,
    AnalyticalObservation,
    InfographicRequirement,
    InfographicPlanning,
    InfographicObservation
)
from memory.database import MemoryManager

class Graph:
    def __init__(
        self,
        context_manager: ContextManager,
        memory_manager: MemoryManager,
        language_models: Dict[Literal["low", "medium", "high"], BaseChatModel]
    ) -> None:
        """
        Initialize the orchestrator with a graph definition.
        """
        self.context_manager: ContextManager = context_manager
        self.memory_manager: MemoryManager = memory_manager
        self.composer: Composer = Composer(context_manager, memory_manager)
        self.low_model: BaseChatModel = language_models["low"]
        self.medium_model: BaseChatModel = language_models["medium"]
        self.high_model: BaseChatModel = language_models["high"]

        self.graph_builder: StateGraph[State, Context] = StateGraph(
            state_schema=State,
            context_schema=Context,
        )

    def intent_comprehension(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_conversation_summary_list()
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message] + state["messages"]

        llm: Runnable = self.low_model.with_structured_output(
            schema=IntentComprehension,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: IntentComprehension = IntentComprehension.model_validate(llm_output)

        return {
            "ui_payload": "",
            "next_node": "request_classification",
            "intent_comprehension": serialized_output
        }

    def request_classification(self, state: State, runtime: Runtime[Context]) -> Command[Literal["punt_response", "analytical_requirement"]]:
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt)
        llm_input: Sequence = [system_message]
        llm_input += self.composer.get_relevant_conversation(state)
        llm_input += state["messages"]

        llm: Runnable = self.low_model.with_structured_output(
            schema=RequestClassification,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: RequestClassification = RequestClassification.model_validate(llm_output)

        if serialized_output.request_is_business_analytical_domain:
            return Command(
                goto="analytical_requirement",
                update={
                    "ui_payload": "",
                    "next_node": "analytical_requirement",
                    "request_classification": serialized_output
                }
            )

        return Command(
            goto="punt_response",
            update={
                "ui_payload": "",
                "next_node": "punt_response",
                "request_classification": serialized_output
            }
        )

    def punt_response(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_punt_response_rationale(state)
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message] + state["messages"]
        llm_output: AIMessage = self.low_model.invoke(llm_input)

        return {
            "ui_payload": "",
            "next_node": None,
            "messages": [llm_output]
        }

    def analytical_requirement(self, state: State, runtime: Runtime[Context]) -> Command[Literal["direct_response", "data_availability"]]:
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt)
        llm_input: Sequence = [system_message]
        llm_input += self.composer.get_relevant_conversation(state)
        llm_input += state["messages"]

        llm: Runnable = self.low_model.with_structured_output(
            schema=AnalyticalRequirement,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: AnalyticalRequirement = AnalyticalRequirement.model_validate(llm_output)

        if serialized_output.analytical_process_is_required:
            return Command(
                goto="data_availability",
                update={
                    "ui_payload": "",
                    "next_node": "data_availability",
                    "analytical_requirement": serialized_output
                }
            )

        return Command(
            goto="direct_response",
            update={
                "ui_payload": "",
                "next_node": "direct_response",
                "analytical_requirement": serialized_output
            }
        )

    def direct_response(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt)
        llm_input: Sequence = [system_message]
        llm_input += self.composer.get_relevant_conversation(state)
        llm_input += state["messages"]
        llm_output: AIMessage = self.low_model.invoke(llm_input)

        return {
            "ui_payload": "",
            "next_node": "summarization",
            "messages": [llm_output]
        }

    def data_availability(self, state: State, runtime: Runtime[Context]) -> Command[Literal["data_unavailability_response", "data_retrieval_planning"]]:
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_database_schema_info()
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]
        llm_input += self.composer.get_relevant_conversation(state)
        llm_input += state["messages"]

        llm: Runnable = self.low_model.with_structured_output(
            schema=DataAvailability,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)

        serialized_output: DataAvailability = DataAvailability.model_validate(llm_output)

        if serialized_output.data_is_available:
            return Command(
                goto="data_retrieval_planning",
                update={
                    "ui_payload": "",
                    "next_node": "data_retrieval_planning",
                    "data_availability": serialized_output
                }
            )

        return Command(
            goto="data_unavailability_response",
            update={
                "ui_payload": "",
                "next_node": "data_unavailability_response",
                "data_availability": serialized_output
            }
        )

    def data_unavailability_response(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_data_unavailability_response_rationale(state)
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]
        llm_input += self.composer.get_relevant_conversation(state)
        llm_input += state["messages"]
        llm_output: AIMessage = self.low_model.invoke(llm_input)

        return {
            "ui_payload": "",
            "next_node": "summarization",
            "messages": [llm_output]
        }

    def data_retrieval_planning(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        system_prompt: str = ""
        context_prompt: str = ""

        if state["data_retrieval_planning"]:
            if state["data_retrieval_execution"]:
                system_prompt += runtime.context.prompts_set[sys._getframe(0).f_code.co_name + "_from_data_retrieval_execution"]
                context_prompt += self.composer.get_database_schema_info()
                context_prompt += self.composer.get_last_generated_sql_query(state)
                context_prompt += self.composer.get_data_retrieval_execution_feedback(state)
            elif state["data_retrieval_observation"]:
                system_prompt += runtime.context.prompts_set[sys._getframe(0).f_code.co_name + "_from_data_retrieval_observation"]
                context_prompt += self.composer.get_database_schema_info()
                context_prompt += self.composer.get_last_generated_sql_query(state)
                context_prompt += self.composer.get_dataframe_schema_info()
                context_prompt += self.composer.get_data_retrieval_observation_feedback(state)
            else:
                raise ValueError("'data_retrieval_planning' is triggered by feedback node. One of these following states should exist: 'data_retrieval_execution' or 'data_retrieval_observation'")
        else:
            system_prompt += runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
            context_prompt += self.composer.get_database_schema_info()

        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]
        llm_input += self.composer.get_relevant_conversation(state)
        llm_input += state["messages"]

        llm: Runnable = self.low_model.with_structured_output(
            schema=DataRetrievalPlanning,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)

        serialized_output: DataRetrievalPlanning = DataRetrievalPlanning.model_validate(llm_output)

        return {
            "ui_payload": "",
            "next_node": "data_retrieval_execution",
            "data_retrieval_planning": serialized_output,
            "data_retrieval_execution": None,
            "data_retrieval_observation": None,
        }

    def data_retrieval_execution(self, state: State) -> Command[Literal["data_retrieval_planning", "data_retrieval_observation"]]:
        if state["data_retrieval_planning"]:
            if state["data_retrieval_planning"].sql_query:
                sql_query: str = state["data_retrieval_planning"].sql_query
                schema: Dict[Literal["tables", "columns"], Union[List, Dict]] = self.context_manager.inspect_external_database()

                if error := self.composer.validate_sql_query(sql_query, schema):
                    return Command(
                        goto="data_retrieval_planning",
                        update={
                            "ui_payload": "",
                            "next_node": "data_retrieval_planning",
                            "data_retrieval_execution": error
                        }
                    )

                if error := self.context_manager.extract_external_database(sql_query):
                    return Command(
                        goto="data_retrieval_planning",
                        update={
                            "ui_payload": "",
                            "next_node": "data_retrieval_planning",
                            "data_retrieval_execution": error
                        }
                    )

                return Command(
                    goto="data_retrieval_observation",
                    update={
                        "ui_payload": "",
                        "next_node": "data_retrieval_observation",
                        "data_retrieval_execution": None
                    }
                )

            raise ValueError("'data_retrival_planning' state does not contain 'sql_query' attribute when retrieving data")
        else:
            raise ValueError(f"'data_retrival_planning' state must not empty in '{sys._getframe(0).f_code.co_name}' node")

    def data_retrieval_observation(self, state: State, runtime: Runtime[Context]) -> Command[Literal["data_retrieval_planning", "analytical_planning"]]:
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_database_schema_info()
        context_prompt += self.composer.get_last_generated_sql_query(state)
        context_prompt += self.composer.get_dataframe_schema_info()
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)
        llm_input: Sequence = [system_message]
        llm_input += self.composer.get_relevant_conversation(state)
        llm_input += state["messages"]

        llm: Runnable = self.low_model.with_structured_output(
            schema=DataRetrievalObservation,
            method="json_schema"
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: DataRetrievalObservation = DataRetrievalObservation.model_validate(llm_output)

        if serialized_output.result_is_sufficient:
            return Command(
                goto="analytical_planning",
                update={
                    "ui_payload": "",
                    "next_node": "analytical_planning",
                    "data_retrieval_observation": serialized_output
                }
            )

        return Command(
            goto="data_retrieval_planning",
            update={
                "ui_payload": "",
                "next_node": "data_retrieval_planning",
                "data_retrieval_observation": serialized_output
            }
        )

    def analytical_planning(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        serialized_output: DataRetrievalPlanning = DataRetrievalPlanning.model_validate({})

        return {
            "ui_payload": "",
            "next_node": "analytical_plan_execution",
            "analytical_planning": serialized_output
        }

    def analytical_plan_execution(self, state: State, runtime: Runtime[Context]) -> Command[Literal["analytical_planning", "analytical_observation"]]:
        sandbox: Sandbox = Sandbox.create()
        execution: Execution = sandbox.run_code("")

        if execution.error:
            return Command(
                goto="analytical_planning",
                update={
                    "ui_payload": "",
                    "next_node": "analytical_planning",
                    "analytical_plan_execution": execution
                }
            )

        return Command(
            goto="analytical_observation",
            update={
                "ui_payload": "",
                "next_node": "analytical_observation",
                "analytical_plan_execution": execution
            }
        )

    def analytical_observation(self, state: State, runtime: Runtime[Context]) -> Command[Literal["analytical_planning", "analytical_result"]]:
        serialized_output: AnalyticalObservation = AnalyticalObservation.model_validate({})

        if serialized_output.result_is_sufficient:
            return Command(
                goto="analytical_result",
                update={
                    "ui_payload": "",
                    "next_node": "analytical_result",
                    "analytical_observation": serialized_output
                }
            )

        return Command(
            goto="analytical_planning",
            update={
                "ui_payload": "",
                "next_node": "analytical_planning",
                "analytical_observation": serialized_output
            }
        )

    def analytical_result(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        return {
            "ui_payload": "",
            "next_node": "infographic_requirement",
            "analytical_result": ""
        }

    def infographic_requirement(self, state: State, runtime: Runtime[Context]) -> Command[Literal["analytical_response", "infographic_planning"]]:
        serialized_output: InfographicRequirement = InfographicRequirement.model_validate({})

        if serialized_output.infographic_is_required:
            return Command(
                goto="analytical_response",
                update={
                    "ui_payload": "",
                    "next_node": "analytical_response",
                    "infographic_requirement": serialized_output
                }
            )

        return Command(
            goto="infographic_planning",
            update={
                "ui_payload": "",
                "next_node": "infographic_planning",
                "infographic_requirement": serialized_output
            }
        )
    
    def analytical_response(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        return {
            "ui_payload": "",
            "next_node": "summarization",
            "messages": []
        }

    def infographic_planning(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        serialized_output: InfographicPlanning = InfographicPlanning.model_validate({})

        return {
            "ui_payload": "",
            "next_node": "infographic_plan_execution",
            "infographic_planning": serialized_output
        }

    def infographic_plan_execution(self, state: State, runtime: Runtime[Context]) -> Command[Literal["infographic_planning", "infographic_observation"]]:
        sandbox: Sandbox = Sandbox.create()
        execution: Execution = sandbox.run_code("")

        if execution.error:
            return Command(
                goto="infographic_planning",
                update={
                    "ui_payload": "",
                    "next_node": "infographic_planning",
                    "infographic_plan_execution": execution
                }
            )

        return Command(
            goto="infographic_observation",
            update={
                "ui_payload": "",
                "next_node": "infographic_observation",
                "infographic_plan_execution": execution
            }
        )

    def infographic_observation(self, state: State, runtime: Runtime[Context]) -> Command[Literal["infographic_planning", "analytical_response"]]:
        serialized_output: InfographicObservation = InfographicObservation.model_validate({})

        if serialized_output.result_is_sufficient:
            return Command(
                goto="analytical_response",
                update={
                    "ui_payload": "",
                    "next_node": "analytical_response",
                    "infographic_observation": serialized_output
                }
            )

        return Command(
            goto="infographic_planning",
            update={
                "ui_payload": "",
                "next_node": "infographic_planning",
                "infographic_observation": serialized_output
            }
        )
    
    def summarization(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        return {}

    def build_graph(self) -> CompiledStateGraph[State, Context]:
        """
        Construct and compile the analytical execution graph.

        This method defines all nodes and edges, producing a compiled
        LangGraph state machine ready for execution.
        """
        self.graph_builder.add_node("intent_comprehension", self.intent_comprehension)
        self.graph_builder.add_node("request_classification", self.request_classification)
        self.graph_builder.add_node("punt_response", self.punt_response)
        self.graph_builder.add_node("analytical_requirement", self.analytical_requirement)
        self.graph_builder.add_node("direct_response", self.direct_response)
        self.graph_builder.add_node("data_availability", self.data_availability)
        self.graph_builder.add_node("data_unavailability_response", self.data_unavailability_response)
        self.graph_builder.add_node("data_retrieval_planning", self.data_retrieval_planning)
        self.graph_builder.add_node("data_retrieval_execution", self.data_retrieval_execution)
        self.graph_builder.add_node("data_retrieval_observation", self.data_retrieval_observation)
        self.graph_builder.add_node("analytical_planning", self.analytical_planning)
        self.graph_builder.add_node("analytical_plan_execution", self.analytical_plan_execution)
        self.graph_builder.add_node("analytical_observation", self.analytical_observation)
        self.graph_builder.add_node("analytical_result", self.analytical_result)
        self.graph_builder.add_node("infographic_requirement", self.infographic_requirement)
        self.graph_builder.add_node("analytical_response", self.analytical_response)
        self.graph_builder.add_node("infographic_planning", self.infographic_planning)
        self.graph_builder.add_node("infographic_plan_execution", self.infographic_plan_execution)
        self.graph_builder.add_node("infographic_observation", self.infographic_observation)
        self.graph_builder.add_node("summarization", self.summarization)

        self.graph_builder.add_edge(START, "intent_comprehension")
        self.graph_builder.add_edge("intent_comprehension", "request_classification")
        self.graph_builder.add_edge("punt_response", END)
        self.graph_builder.add_edge("direct_response", "summarization")
        self.graph_builder.add_edge("data_unavailability_response", "summarization")
        self.graph_builder.add_edge("data_retrieval_planning", "data_retrieval_execution")
        self.graph_builder.add_edge("analytical_planning", "analytical_plan_execution")
        self.graph_builder.add_edge("analytical_result", "infographic_requirement")
        self.graph_builder.add_edge("analytical_response", "summarization")
        self.graph_builder.add_edge("infographic_planning", "infographic_plan_execution")
        self.graph_builder.add_edge("summarization", END)

        return self.graph_builder.compile()
