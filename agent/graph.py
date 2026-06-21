# pyright: reportPrivateUsage=false
# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false

# standard
import sys
from typing import (
    Any,
    Literal,
    cast,
)

# third-party
from e2b_code_interpreter import Execution
from e2b_code_interpreter.code_interpreter_sync import (
    Sandbox,
)
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import (
    StateGraph,
    END,
    START,
)
from langgraph.graph.state import (
    CompiledStateGraph,
)
from langgraph.runtime import Runtime
from langgraph.types import Command, interrupt

# internal
from .composer import Composer
from .state import State
from .runtime import Context
from context import ContextManager
from context.database import external_db_url
from language_model.provider import groq_gpt_120b_high, groq_qwen
from language_model.schema import (
    IntentComprehension,
    RequestClassification,
    AnalyticalRequirement,
    DataAvailability,
    DataRetrievalPlan,
    DataRetrievalPlanObservation,
    AnalyticalPlan,
    AnalyticalPlanObservation,
)
from memory import MemoryManager
from memory.database import internal_db_url

MAX_CORRECTION_RETRIES: int = 3


class Graph:
    def __init__(self) -> None:
        """
        Initialize the Graph class.
        """
        self.composer: Composer = Composer(
            context_manager=ContextManager(external_db_url),
            memory_manager=MemoryManager(internal_db_url),
            default_model=groq_gpt_120b_high,
        )

        self.graph_builder: StateGraph[State, Context, State, State] = StateGraph(
            state_schema=State,
            context_schema=Context,
        )

    def __intent_comprehension(self, state: State, runtime: Runtime[Context]) -> dict[str, Any]:
        """
        Node to handle intent comprehension.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_conversation_summary_list()
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)

        llm, llm_input = self.composer.get_runnable_with_input(
            system_message=system_message,
            state=state,
            schema=IntentComprehension,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: IntentComprehension = IntentComprehension.model_validate(llm_output)

        return {
            "ui_payload": "Identifying request category...",
            "current_node": "request_classification",
            "intent_comprehension": serialized_output,
        }

    def __request_classification(
        self, state: State, runtime: Runtime[Context]
    ) -> Command[
        Literal[
            "punt_response",
            "context_distillation",
        ]
    ]:
        """
        Node to handle request classification.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_conversation_summary_list()
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)

        llm, llm_input = self.composer.get_runnable_with_input(
            system_message=system_message,
            state=state,
            schema=RequestClassification,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: RequestClassification = RequestClassification.model_validate(llm_output)

        if serialized_output.request_is_business_analytical_domain:
            return Command(
                goto="context_distillation",
                update={
                    "ui_payload": "Refining request...",
                    "current_node": "context_distillation",
                    "request_classification": serialized_output,
                },
            )

        return Command(
            goto="punt_response",
            update={
                "ui_payload": "Wrapping up...",
                "current_node": "punt_response",
                "request_classification": serialized_output,
            },
        )

    def __punt_response(self, state: State, runtime: Runtime[Context]) -> dict[str, Any]:
        """
        Node to handle punt response.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_punt_response_feedback(state)
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)

        llm, llm_input = self.composer.get_runnable_with_input(
            system_message=system_message,
            state=state,
        )

        llm_output: AIMessage = cast(AIMessage, llm.invoke(llm_input))

        return {
            "ui_payload": "Ready to go!",
            "current_node": None,
            "messages": [llm_output],
        }

    def __context_distillation(self, state: State, runtime: Runtime[Context]) -> dict[str, Any]:
        """
        Node to handle context distillation.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt)

        llm, llm_input = self.composer.get_runnable_with_input(
            system_message=system_message,
            state=state,
        )

        llm_output: AIMessage = cast(AIMessage, llm.invoke(llm_input))

        return {
            "ui_payload": "Surveying database landscape...",
            "current_node": "data_availability",
            "context_distillation": llm_output,
        }

    def __analytical_requirement(
        self,
        state: State,
        runtime: Runtime[Context],
    ) -> Command[Literal["direct_response", "data_availability"]]:
        """
        Node to handle analytical requirement.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_conversation_summary_list()
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)

        llm, llm_input = self.composer.get_runnable_with_input(
            system_message=system_message,
            state=state,
            schema=AnalyticalRequirement,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: AnalyticalRequirement = AnalyticalRequirement.model_validate(llm_output)

        if serialized_output.analytical_process_is_required:
            return Command(
                goto="data_availability",
                update={
                    "ui_payload": "",
                    "current_node": "data_availability",
                    "analytical_requirement": serialized_output,
                },
            )

        return Command(
            goto="direct_response",
            update={
                "ui_payload": "Wrapping up...",
                "current_node": "direct_response",
                "analytical_requirement": serialized_output,
            },
        )

    def __direct_response(self, state: State, runtime: Runtime[Context]) -> dict[str, Any]:
        """
        Node to handle direct response.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt)

        llm, llm_input = self.composer.get_runnable_with_input(
            system_message=system_message,
            state=state,
        )

        llm_output: AIMessage = cast(AIMessage, llm.invoke(llm_input))

        return {
            "ui_payload": "Ready to go!",
            "current_node": "summarization",
            "messages": [llm_output],
        }

    def __data_availability(
        self, state: State, runtime: Runtime[Context]
    ) -> Command[
        Literal[
            "data_unavailability_response",
            "data_retrieval_plan",
        ]
    ]:
        """
        Node to handle data availability.

        On first visit (from analytical_requirement), the LLM evaluates
        whether the database schema can satisfy the request.

        On retry-exhausted re-visit (from data_retrieval_plan), the node
        pauses via interrupt() to request additional context from the user
        before re-evaluating.
        """
        additional_context: str | None = None

        if state["data_retrieval_retry_count"] >= MAX_CORRECTION_RETRIES:
            system_prompt = runtime.context.prompts_set[sys._getframe(0).f_code.co_name + "_from_data_retrieval_plan"]

            context_prompt = self.composer.get_data_retrieval_failure_summary(state)
            system_message = SystemMessage(system_prompt + context_prompt)

            llm, llm_input = self.composer.get_runnable_with_input(
                system_message=system_message,
                state=state,
            )

            summary_output: AIMessage = cast(AIMessage, llm.invoke(llm_input))
            interrupt_message: str = summary_output.content if isinstance(summary_output.content, str) else ""
            additional_context = interrupt(interrupt_message)

        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_database_schema_info()

        if additional_context:
            context_prompt += (
                f"\n\nAdditional context provided by the user after failed retrieval attempts: {additional_context}"
            )

        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)

        llm, llm_input = self.composer.get_runnable_with_input(
            system_message=system_message,
            state=state,
            schema=DataAvailability,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: DataAvailability = DataAvailability.model_validate(llm_output)

        if serialized_output.data_is_available:
            update: dict[str, Any] = {
                "ui_payload": "Structuring data fetch...",
                "current_node": "data_retrieval_plan",
                "data_availability": serialized_output,
            }

            if additional_context:
                update["messages"] = [HumanMessage(content=additional_context)]
                update["data_retrieval_retry_count"] = 0
                update["data_retrieval_failure_history"] = []

            return Command(goto="data_retrieval_plan", update=update)

        return Command(
            goto="data_unavailability_response",
            update={
                "ui_payload": "Wrapping up...",
                "current_node": "data_unavailability_response",
                "data_availability": serialized_output,
            },
        )

    def __data_unavailability_response(self, state: State, runtime: Runtime[Context]) -> dict[str, Any]:
        """
        Node to handle data unavailability response.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_data_unavailability_response_feedback(state)
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)

        llm, llm_input = self.composer.get_runnable_with_input(
            system_message=system_message,
            state=state,
        )

        llm_output: AIMessage = cast(AIMessage, llm.invoke(llm_input))

        return {
            "ui_payload": "Ready to go!",
            "current_node": "summarization",
            "messages": [llm_output],
        }

    def __data_retrieval_plan(
        self, state: State, runtime: Runtime[Context]
    ) -> Command[
        Literal[
            "data_retrieval_plan_execution",
            "data_availability",
        ]
    ]:
        """
        Node to handle data retrieval plan.
        """
        if state["data_retrieval_retry_count"] >= MAX_CORRECTION_RETRIES:
            return Command(
                goto="data_availability",
                update={
                    "ui_payload": "Requesting additional context...",
                    "current_node": "data_availability",
                },
            )

        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_database_schema_info()

        if state["data_retrieval_plan"]:
            context_prompt += self.composer.get_data_retrieval_plan(state)

        if state["data_retrieval_plan_execution"]:
            system_prompt = runtime.context.prompts_set[
                sys._getframe(0).f_code.co_name + "_from_data_retrieval_plan_execution"
            ]

            context_prompt += self.composer.get_data_retrieval_plan_execution_feedback(state)

        if state["data_retrieval_plan_observation"]:
            system_prompt = runtime.context.prompts_set[
                sys._getframe(0).f_code.co_name + "_from_data_retrieval_plan_observation"
            ]

            context_prompt += self.composer.get_dataframe_schema_info()
            context_prompt += self.composer.get_data_retrieval_plan_observation_feedback(state)

        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)

        llm, llm_input = self.composer.get_runnable_with_input(
            system_message=system_message,
            state=state,
            schema=DataRetrievalPlan,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: DataRetrievalPlan = DataRetrievalPlan.model_validate(llm_output)

        return Command(
            goto="data_retrieval_plan_execution",
            update={
                "ui_payload": "Implementing retrieval plan...",
                "current_node": "data_retrieval_plan_execution",
                "data_retrieval_plan": serialized_output,
                "data_retrieval_plan_execution": None,
                "data_retrieval_plan_observation": None,
            },
        )

    def __data_retrieval_plan_execution(
        self, state: State
    ) -> Command[
        Literal[
            "data_retrieval_plan",
            "data_retrieval_plan_observation",
        ]
    ]:
        """
        Node to handle data retrieval plan execution.
        """
        if error := self.composer.validate_sql_query(state):
            return Command(
                goto="data_retrieval_plan",
                update={
                    "ui_payload": "Refining retrieval strategy...",
                    "current_node": "data_retrieval_plan",
                    "data_retrieval_plan_execution": error,
                    "data_retrieval_retry_count": state["data_retrieval_retry_count"] + 1,
                    "data_retrieval_failure_history": [
                        *state["data_retrieval_failure_history"],
                        f"SQL validation error: {error}",
                    ],
                },
            )

        if error := self.composer.extract_external_database(state):
            return Command(
                goto="data_retrieval_plan",
                update={
                    "ui_payload": "Refining retrieval strategy...",
                    "current_node": "data_retrieval_plan",
                    "data_retrieval_plan_execution": error,
                    "data_retrieval_retry_count": state["data_retrieval_retry_count"] + 1,
                    "data_retrieval_failure_history": [
                        *state["data_retrieval_failure_history"],
                        f"Database extraction error: {error}",
                    ],
                },
            )

        return Command(
            goto="data_retrieval_plan_observation",
            update={
                "ui_payload": "Auditing data integrity...",
                "current_node": "data_retrieval_plan_observation",
            },
        )

    def __data_retrieval_plan_observation(
        self, state: State, runtime: Runtime[Context]
    ) -> Command[
        Literal[
            "data_retrieval_plan",
            "analytical_plan",
        ]
    ]:
        """
        Node to handle data retrieval plan observation.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_database_schema_info()
        context_prompt += self.composer.get_data_retrieval_plan(state)
        context_prompt += self.composer.get_dataframe_schema_info()
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)

        llm, llm_input = self.composer.get_runnable_with_input(
            system_message=system_message,
            state=state,
            schema=DataRetrievalPlanObservation,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: DataRetrievalPlanObservation = DataRetrievalPlanObservation.model_validate(llm_output)

        if serialized_output.result_is_sufficient:
            return Command(
                goto="analytical_plan",
                update={
                    "ui_payload": "Formulating analytical steps...",
                    "current_node": "analytical_plan",
                    "data_retrieval_plan_observation": serialized_output,
                },
            )

        return Command(
            goto="data_retrieval_plan",
            update={
                "ui_payload": "Refining retrieval strategy...",
                "current_node": "data_retrieval_plan",
                "data_retrieval_plan_observation": serialized_output,
                "data_retrieval_retry_count": state["data_retrieval_retry_count"] + 1,
                "data_retrieval_failure_history": [
                    *state["data_retrieval_failure_history"],
                    f"Observation deemed insufficient: {serialized_output.rationale}",
                ],
            },
        )

    def __analytical_plan(self, state: State, runtime: Runtime[Context]) -> dict[str, Any]:
        """
        Node to handle analytical plan.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_database_schema_info()
        context_prompt += self.composer.get_data_retrieval_plan(state)
        context_prompt += self.composer.get_dataframe_schema_info()

        if state["analytical_plan"]:
            context_prompt += self.composer.get_analytical_plan(state, original=True)

        if state["analytical_plan_execution"]:
            system_prompt = runtime.context.prompts_set[
                sys._getframe(0).f_code.co_name + "_from_analytical_plan_execution"
            ]

            context_prompt += self.composer.get_analytical_plan_execution_feedback(state)

        if state["analytical_plan_observation"]:
            system_prompt = runtime.context.prompts_set[
                sys._getframe(0).f_code.co_name + "_from_analytical_plan_observation"
            ]

            context_prompt += self.composer.get_analytical_plan_observation_feedback(state)

        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)

        llm, llm_input = self.composer.get_runnable_with_input(
            system_message=system_message,
            state=state,
            schema=AnalyticalPlan,
            model=groq_qwen,
            structured_output_method="function_calling",
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: AnalyticalPlan = AnalyticalPlan.model_validate(llm_output)

        for analytical_step in serialized_output.plan:
            analytical_step.python_code = analytical_step.python_code.replace("\\n", "\n")

        return {
            "ui_payload": "Running analysis sequence...",
            "current_node": "analytical_plan_execution",
            "analytical_plan": serialized_output,
            "analytical_plan_execution": None,
            "analytical_plan_observation": None,
        }

    def __analytical_plan_execution(
        self,
        state: State,
        runtime: Runtime[Context],
    ) -> Command[
        Literal[
            "analytical_plan",
            "analytical_plan_observation",
        ]
    ]:
        """
        Node to handle analytical plan execution.
        """
        sandbox: Sandbox = self.composer.prepare_sandbox_environment()
        code: str = self.composer.get_analytical_python_code(state, runtime)
        execution: Execution = sandbox.run_code(code)
        sandbox.kill()

        if execution.error:
            return Command(
                goto="analytical_plan",
                update={
                    "ui_payload": "Recalibrating analytical logic...",
                    "current_node": "analytical_plan",
                    "analytical_plan_execution": execution,
                },
            )

        return Command(
            goto="analytical_plan_observation",
            update={
                "ui_payload": "Auditing insights...",
                "current_node": "analytical_plan_observation",
                "analytical_plan_execution": execution,
            },
        )

    def __analytical_plan_observation(
        self,
        state: State,
        runtime: Runtime[Context],
    ) -> Command[
        Literal[
            "analytical_plan",
            "analytical_response",
        ]
    ]:
        """
        Node to handle analytical plan observation.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_database_schema_info()
        context_prompt += self.composer.get_data_retrieval_plan(state)
        context_prompt += self.composer.get_dataframe_schema_info()
        context_prompt += self.composer.get_analytical_plan(state)
        context_prompt += self.composer.get_analytical_plan_execution_result(state)
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)

        llm, llm_input = self.composer.get_runnable_with_input(
            system_message=system_message,
            state=state,
            schema=AnalyticalPlanObservation,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: AnalyticalPlanObservation = AnalyticalPlanObservation.model_validate(llm_output)

        if serialized_output.result_is_sufficient:
            return Command(
                goto="analytical_response",
                update={
                    "ui_payload": "Structuring insight...",
                    "current_node": "analytical_response",
                    "analytical_plan_observation": serialized_output,
                },
            )

        return Command(
            goto="analytical_plan",
            update={
                "ui_payload": "Enhancing analytical precision...",
                "current_node": "analytical_plan",
                "analytical_plan_execution": None,
                "analytical_plan_observation": serialized_output,
            },
        )

    def __analytical_response(self, state: State, runtime: Runtime[Context]) -> dict[str, Any]:
        """
        Node to synthesize validated analytical execution into an interpretable response.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_analytical_plan(state)
        context_prompt += self.composer.get_analytical_plan_execution_result(state)
        context_prompt += self.composer.get_analytical_plan_observation_result(state)
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)

        llm, llm_input = self.composer.get_runnable_with_input(
            system_message=system_message,
            state=state,
        )

        llm_output: AIMessage = cast(AIMessage, llm.invoke(llm_input))

        return {
            "ui_payload": "Ready to go!",
            "current_node": "summarization",
            "messages": [llm_output],
        }

    def __summarization(self, state: State, runtime: Runtime[Context]) -> dict[str, Any]:
        """
        Node to handle summarization.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt)

        llm, llm_input = self.composer.get_runnable_with_input(
            system_message=system_message,
            state=state,
        )

        llm_output: AIMessage = cast(AIMessage, llm.invoke(llm_input))

        self.composer.save_current_interaction(
            state=state,
            llm_output=llm_output,
            turn_num=runtime.context.turn_num,
        )

        return {
            "current_node": None,
            "summarization": llm_output,
        }

    def build_graph(
        self,
    ) -> CompiledStateGraph[State, Context]:
        """
        Construct and compile the analytical execution graph.
        """
        self.graph_builder.add_node(
            node="intent_comprehension",
            action=self.__intent_comprehension,
        )

        self.graph_builder.add_node(
            node="request_classification",
            action=self.__request_classification,
        )

        self.graph_builder.add_node(
            node="punt_response",
            action=self.__punt_response,
        )

        self.graph_builder.add_node(
            node="context_distillation",
            action=self.__context_distillation,
        )

        self.graph_builder.add_node(
            node="analytical_requirement",
            action=self.__analytical_requirement,
        )

        self.graph_builder.add_node(
            node="direct_response",
            action=self.__direct_response,
        )

        self.graph_builder.add_node(
            node="data_availability",
            action=self.__data_availability,
        )

        self.graph_builder.add_node(
            node="data_unavailability_response",
            action=self.__data_unavailability_response,
        )

        self.graph_builder.add_node(
            node="data_retrieval_plan",
            action=self.__data_retrieval_plan,
        )

        self.graph_builder.add_node(
            node="data_retrieval_plan_execution",
            action=self.__data_retrieval_plan_execution,
        )

        self.graph_builder.add_node(
            node="data_retrieval_plan_observation",
            action=self.__data_retrieval_plan_observation,
        )

        self.graph_builder.add_node(
            node="analytical_plan",
            action=self.__analytical_plan,
        )

        self.graph_builder.add_node(
            node="analytical_plan_execution",
            action=self.__analytical_plan_execution,
        )

        self.graph_builder.add_node(
            node="analytical_plan_observation",
            action=self.__analytical_plan_observation,
        )

        self.graph_builder.add_node(
            node="analytical_response",
            action=self.__analytical_response,
        )

        self.graph_builder.add_node(node="summarization", action=self.__summarization)

        self.graph_builder.add_edge(start_key=START, end_key="intent_comprehension")

        self.graph_builder.add_edge(
            start_key="intent_comprehension",
            end_key="request_classification",
        )

        self.graph_builder.add_edge(start_key="punt_response", end_key=END)

        self.graph_builder.add_edge(start_key="direct_response", end_key="summarization")

        self.graph_builder.add_edge(start_key="context_distillation", end_key="analytical_requirement")

        self.graph_builder.add_edge(
            start_key="data_unavailability_response",
            end_key="summarization",
        )

        self.graph_builder.add_edge(
            start_key="analytical_plan",
            end_key="analytical_plan_execution",
        )

        self.graph_builder.add_edge(start_key="analytical_response", end_key="summarization")
        self.graph_builder.add_edge(start_key="summarization", end_key=END)

        return self.graph_builder.compile(checkpointer=MemorySaver())
