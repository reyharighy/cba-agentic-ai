# pyright: reportPrivateUsage=false
# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false

# standard
import sys
from pathlib import Path
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
from langchain_core.language_models.chat_models import (
    BaseChatModel,
)
from langchain_core.messages import (
    AIMessage,
    SystemMessage,
)
from langgraph.graph import (
    StateGraph,
    END,
    START,
)
from langgraph.graph.state import (
    CompiledStateGraph,
)
from langgraph.runtime import Runtime
from langgraph.types import Command

# internal
from .composer import Composer
from .runtime import Context
from .state import State
from context.database import ContextManager
from context.datasets import dataset_file_path
from language_model.schema import (
    IntentComprehension,
    RequestClassification,
    AnalyticalRequirement,
    DataAvailability,
    DataRetrievalPlan,
    DataRetrievalPlanObservation,
    AnalyticalPlan,
    AnalyticalPlanObservation,
    InfographicRequirement,
    InfographicPlan,
    InfographicPlanObservation,
)
from memory.database import MemoryManager
from memory.infographic import (
    infographic_dir_path,
)
from memory.models import (
    ChatHistoryCreate,
    ShortMemoryCreate,
)


class Graph:
    def __init__(
        self, context_manager: ContextManager, memory_manager: MemoryManager, language_model: BaseChatModel
    ) -> None:
        """
        Initialize the Graph class.
        """
        self.context_manager: ContextManager = context_manager
        self.memory_manager: MemoryManager = memory_manager
        self.composer: Composer = Composer(context_manager, memory_manager)
        self.language_model: BaseChatModel = language_model

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

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
            schema=IntentComprehension,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: IntentComprehension = IntentComprehension.model_validate(llm_output)

        return {
            "ui_payload": "Identifying request category...",
            "next_node": "request_classification",
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
        system_message: SystemMessage = SystemMessage(system_prompt)

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
            schema=RequestClassification,
            include_conversation=True,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: RequestClassification = RequestClassification.model_validate(llm_output)

        if serialized_output.request_is_business_analytical_domain:
            return Command(
                goto="context_distillation",
                update={
                    "ui_payload": "Refining request...",
                    "next_node": "context_distillation",
                    "request_classification": serialized_output,
                },
            )

        return Command(
            goto="punt_response",
            update={
                "ui_payload": "Wrapping up...",
                "next_node": "punt_response",
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

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
        )

        llm_output: AIMessage = cast(AIMessage, llm.invoke(llm_input))

        return {
            "ui_payload": "Ready to go!",
            "next_node": None,
            "messages": [llm_output],
        }

    def __context_distillation(self, state: State, runtime: Runtime[Context]) -> dict[str, Any]:
        """
        Node to handle context distillation.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt)

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
            include_conversation=True,
        )

        llm_output: AIMessage = cast(AIMessage, llm.invoke(llm_input))

        return {
            "ui_payload": "Surveying database landscape...",
            "next_node": "data_availability",
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
        system_message: SystemMessage = SystemMessage(system_prompt)

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
            schema=AnalyticalRequirement,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: AnalyticalRequirement = AnalyticalRequirement.model_validate(llm_output)

        if serialized_output.analytical_process_is_required:
            return Command(
                goto="data_availability",
                update={
                    "ui_payload": "",
                    "next_node": "data_availability",
                    "analytical_requirement": serialized_output,
                },
            )

        return Command(
            goto="direct_response",
            update={
                "ui_payload": "Wrapping up...",
                "next_node": "direct_response",
                "analytical_requirement": serialized_output,
            },
        )

    def __direct_response(self, state: State, runtime: Runtime[Context]) -> dict[str, Any]:
        """
        Node to handle direct response.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt)

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
            include_conversation=True,
        )

        llm_output: AIMessage = cast(AIMessage, llm.invoke(llm_input))

        return {
            "ui_payload": "Ready to go!",
            "next_node": "summarization",
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
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_database_schema_info()
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
            schema=DataAvailability,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: DataAvailability = DataAvailability.model_validate(llm_output)

        if serialized_output.data_is_available:
            return Command(
                goto="data_retrieval_plan",
                update={
                    "ui_payload": "Structuring data fetch...",
                    "next_node": "data_retrieval_plan",
                    "data_availability": serialized_output,
                },
            )

        return Command(
            goto="data_unavailability_response",
            update={
                "ui_payload": "Wrapping up...",
                "next_node": "data_unavailability_response",
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

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
            include_conversation=True,
        )

        llm_output: AIMessage = cast(AIMessage, llm.invoke(llm_input))

        return {
            "ui_payload": "Ready to go!",
            "next_node": "summarization",
            "messages": [llm_output],
        }

    def __data_retrieval_plan(self, state: State, runtime: Runtime[Context]) -> dict[str, Any]:
        """
        Node to handle data retrieval plan.
        """
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

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
            schema=DataRetrievalPlan,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: DataRetrievalPlan = DataRetrievalPlan.model_validate(llm_output)

        return {
            "ui_payload": "Implementing retrieval plan...",
            "next_node": "data_retrieval_plan_execution",
            "data_retrieval_plan": serialized_output,
            "data_retrieval_plan_execution": None,
            "data_retrieval_plan_observation": None,
        }

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
        if state["data_retrieval_plan"]:
            if state["data_retrieval_plan"].sql_query:
                sql_query: str = state["data_retrieval_plan"].sql_query
                schema: dict[str, list[dict[str, Any]]] = self.context_manager.inspect_external_database()

                if error := self.composer.validate_sql_query(sql_query, schema):
                    return Command(
                        goto="data_retrieval_plan",
                        update={
                            "ui_payload": "Refining retrieval strategy...",
                            "next_node": "data_retrieval_plan",
                            "data_retrieval_plan_execution": error,
                        },
                    )

                if error := self.context_manager.extract_external_database(sql_query):
                    return Command(
                        goto="data_retrieval_plan",
                        update={
                            "ui_payload": "Refining retrieval strategy...",
                            "next_node": "data_retrieval_plan",
                            "data_retrieval_plan_execution": error,
                        },
                    )

                return Command(
                    goto="data_retrieval_plan_observation",
                    update={
                        "ui_payload": "Auditing data integrity...",
                        "next_node": "data_retrieval_plan_observation",
                    },
                )

            raise ValueError("'data_retrieval_plan' state does not contain 'sql_query' attribute when retrieving data")
        else:
            raise ValueError(
                f"'data_retrieval_plan' state must not be empty in '{sys._getframe(0).f_code.co_name}' node"
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

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
            schema=DataRetrievalPlanObservation,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: DataRetrievalPlanObservation = DataRetrievalPlanObservation.model_validate(llm_output)

        if serialized_output.result_is_sufficient:
            return Command(
                goto="analytical_plan",
                update={
                    "ui_payload": "Formulating analytical steps...",
                    "next_node": "analytical_plan",
                    "data_retrieval_plan_observation": serialized_output,
                },
            )

        return Command(
            goto="data_retrieval_plan",
            update={
                "ui_payload": "Refining retrieval strategy...",
                "next_node": "data_retrieval_plan",
                "data_retrieval_plan_observation": serialized_output,
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

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
            schema=AnalyticalPlan,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: AnalyticalPlan = AnalyticalPlan.model_validate(llm_output)

        for analytical_step in serialized_output.plan:
            analytical_step.python_code = analytical_step.python_code.replace("\\n", "\n")

        return {
            "ui_payload": "Running analysis sequence...",
            "next_node": "analytical_plan_execution",
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
                    "next_node": "analytical_plan",
                    "analytical_plan_execution": execution,
                },
            )

        return Command(
            goto="analytical_plan_observation",
            update={
                "ui_payload": "Auditing insights...",
                "next_node": "analytical_plan_observation",
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
            "analytical_result",
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

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
            schema=AnalyticalPlanObservation,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: AnalyticalPlanObservation = AnalyticalPlanObservation.model_validate(llm_output)

        if serialized_output.result_is_sufficient:
            return Command(
                goto="analytical_result",
                update={
                    "ui_payload": "Structuring insight...",
                    "next_node": "analytical_result",
                    "analytical_plan_observation": serialized_output,
                },
            )

        return Command(
            goto="analytical_plan",
            update={
                "ui_payload": "Enhancing analytical precision...",
                "next_node": "analytical_plan",
                "analytical_plan_execution": None,
                "analytical_plan_observation": serialized_output,
            },
        )

    def __analytical_result(self, state: State, runtime: Runtime[Context]) -> dict[str, Any]:
        """
        Node to handle analytical result.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_analytical_plan(state)
        context_prompt += self.composer.get_analytical_plan_execution_result(state)
        context_prompt += self.composer.get_analytical_plan_observation_result(state)
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
            include_conversation=True,
        )

        llm_output: AIMessage = cast(AIMessage, llm.invoke(llm_input))

        return {
            "ui_payload": "Identifying visual opportunities...",
            "next_node": "infographic_requirement",
            "analytical_result": llm_output,
        }

    def __infographic_requirement(
        self, state: State, runtime: Runtime[Context]
    ) -> Command[
        Literal[
            "analytical_response",
            "infographic_plan",
        ]
    ]:
        """
        Node to handle infographic requirement.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        system_message: SystemMessage = SystemMessage(system_prompt)

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
            schema=InfographicRequirement,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: InfographicRequirement = InfographicRequirement.model_validate(llm_output)

        if serialized_output.infographic_is_required:
            return Command(
                goto="infographic_plan",
                update={
                    "ui_payload": "Architecting chart schema...",
                    "next_node": "infographic_plan",
                    "infographic_requirement": serialized_output,
                },
            )

        return Command(
            goto="analytical_response",
            update={
                "ui_payload": "Wrapping up...",
                "next_node": "analytical_response",
                "infographic_requirement": serialized_output,
            },
        )

    def __analytical_response(self, state: State) -> dict[str, Any]:
        """
        Node to handle analytical response.
        """
        return {
            "ui_payload": "Ready to go!",
            "next_node": "summarization",
            "messages": [state["analytical_result"]],
        }

    def __infographic_plan(self, state: State, runtime: Runtime[Context]) -> dict[str, Any]:
        """
        Node to handle infographic plan.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_database_schema_info()
        context_prompt += self.composer.get_data_retrieval_plan(state)
        context_prompt += self.composer.get_dataframe_schema_info()
        context_prompt += self.composer.get_infographic_requirement_rationale(state)

        if state["infographic_plan"]:
            context_prompt += self.composer.get_infographic_plan(state)

        if state["infographic_plan_execution"]:
            system_prompt = runtime.context.prompts_set[
                sys._getframe(0).f_code.co_name + "_from_infographic_plan_execution"
            ]

            context_prompt += self.composer.get_infographic_plan_execution_feedback(state)

        if state["infographic_plan_observation"]:
            system_prompt = runtime.context.prompts_set[
                sys._getframe(0).f_code.co_name + "_from_infographic_plan_observation"
            ]

            context_prompt += self.composer.get_infographic_plan_observation_feedback(state)

        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
            schema=InfographicPlan,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: InfographicPlan = InfographicPlan.model_validate(llm_output)
        serialized_output.python_code = serialized_output.python_code.replace("\\n", "\n")

        return {
            "ui_payload": "Painting insight canvas...",
            "next_node": "infographic_plan_execution",
            "infographic_plan": serialized_output,
            "infographic_plan_execution": None,
            "infographic_plan_observation": None,
        }

    def __infographic_plan_execution(
        self, state: State, runtime: Runtime[Context]
    ) -> Command[
        Literal[
            "infographic_plan",
            "infographic_plan_observation",
        ]
    ]:
        """
        Node to handle infographic plan execution.
        """
        sandbox: Sandbox = self.composer.prepare_sandbox_environment()
        code: str = self.composer.get_infographic_python_code(state, runtime, on_sandbox=True)
        execution: Execution = sandbox.run_code(code)
        sandbox.kill()

        if execution.error:
            return Command(
                goto="infographic_plan",
                update={
                    "ui_payload": "Recalibrating visual map...",
                    "next_node": "infographic_plan",
                    "infographic_plan_execution": execution,
                },
            )

        if state["infographic_plan"]:
            infographic_file_path: Path = Path(
                infographic_dir_path / f"turn_num_{runtime.context.turn_num + 1}" / "infographic.py"
            )

            if not infographic_file_path.parent.exists():
                infographic_file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(dataset_file_path, "rb") as dataset_file:
                with open(infographic_file_path.parent / "dataset.csv", "xb") as file:
                    file.write(dataset_file.read())

            with open(infographic_file_path, "x", encoding="utf-8") as file:
                content: str = "import streamlit as st\n" # decouple this segment
                content += "from pathlib import Path\n"
                content += self.composer.get_infographic_python_code(state, runtime)
                content += "\nst.plotly_chart(fig, on_select='ignore')\n"
                content_list = content.split("\n")

                for index, line in enumerate(content_list):
                    if line == "df = pd.read_csv('dataset.csv')":
                        content_list[index] = "df = pd.read_csv(Path(__file__).parent / 'dataset.csv')"
                        break

                file.write("\n".join(content_list))
        else:
            raise ValueError(f"'infographic_plan' state must not be empty in '{sys._getframe(0).f_code.co_name}' node")

        return Command(
            goto="infographic_plan_observation",
            update={
                "ui_payload": "Evaluating graphic fidelity...",
                "next_node": "infographic_plan_observation",
            },
        )

    def __infographic_plan_observation(
        self, state: State, runtime: Runtime[Context]
    ) -> Command[
        Literal[
            "infographic_plan",
            "analytical_response",
        ]
    ]:
        """
        Node to handle infographic plan observation.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = self.composer.get_database_schema_info()
        context_prompt += self.composer.get_data_retrieval_plan(state)
        context_prompt += self.composer.get_dataframe_schema_info()
        context_prompt += self.composer.get_infographic_requirement_rationale(state)
        context_prompt += self.composer.get_infographic_plan(state)
        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
            schema=InfographicPlanObservation,
        )

        llm_output = llm.invoke(llm_input)
        serialized_output: InfographicPlanObservation = InfographicPlanObservation.model_validate(llm_output)

        if serialized_output.result_is_sufficient:
            return Command(
                goto="analytical_response",
                update={
                    "ui_payload": "Wrapping up...",
                    "next_node": "analytical_response",
                    "infographic_plan_observation": serialized_output,
                },
            )

        return Command(
            goto="infographic_plan",
            update={
                "ui_payload": "Refining the visual blueprint...",
                "next_node": "infographic_plan",
                "infographic_plan_observation": serialized_output,
            },
        )

    def __summarization(self, state: State, runtime: Runtime[Context]) -> dict[str, Any]:
        """
        Node to handle summarization.
        """
        system_prompt: str = runtime.context.prompts_set[sys._getframe(0).f_code.co_name]
        context_prompt: str = ""

        if state["infographic_requirement"] and state["infographic_requirement"].infographic_is_required:
            context_prompt += self.composer.get_infographic_plan(state)

        system_message: SystemMessage = SystemMessage(system_prompt + context_prompt)

        llm, llm_input = self.composer.prepare_invocation(
            system_message=system_message,
            state=state,
            language_model=self.language_model,
            include_conversation=True,
        )

        llm_output: AIMessage = cast(AIMessage, llm.invoke(llm_input))
        turn_num = runtime.context.turn_num + 1

        create_chat_history_params: ChatHistoryCreate = ChatHistoryCreate(
            turn_num=turn_num,
            role="Human",
            content=cast(str, state["messages"][0].content),
        )

        self.memory_manager.store_chat_history(create_chat_history_params())

        create_chat_history_params = ChatHistoryCreate(
            turn_num=turn_num,
            role="AI",
            content=cast(
                str,
                state["messages"][1].content,
            ),
        )

        self.memory_manager.store_chat_history(create_chat_history_params())

        create_short_memory_params: ShortMemoryCreate = ShortMemoryCreate(
            turn_num=turn_num,
            summary=cast(str, llm_output.content),
        )

        self.memory_manager.store_short_memory(create_short_memory_params())

        dataset_file_path.unlink()

        return {"summarization": llm_output}

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
            node="analytical_result",
            action=self.__analytical_result,
        )

        self.graph_builder.add_node(
            node="infographic_requirement",
            action=self.__infographic_requirement,
        )

        self.graph_builder.add_node(
            node="analytical_response",
            action=self.__analytical_response,
        )

        self.graph_builder.add_node(
            node="infographic_plan",
            action=self.__infographic_plan,
        )

        self.graph_builder.add_node(
            node="infographic_plan_execution",
            action=self.__infographic_plan_execution,
        )

        self.graph_builder.add_node(
            node="infographic_plan_observation",
            action=self.__infographic_plan_observation,
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
            start_key="data_retrieval_plan",
            end_key="data_retrieval_plan_execution",
        )

        self.graph_builder.add_edge(
            start_key="analytical_plan",
            end_key="analytical_plan_execution",
        )

        self.graph_builder.add_edge(
            start_key="analytical_result",
            end_key="infographic_requirement",
        )

        self.graph_builder.add_edge(start_key="analytical_response", end_key="summarization")

        self.graph_builder.add_edge(
            start_key="infographic_plan",
            end_key="infographic_plan_execution",
        )

        self.graph_builder.add_edge(start_key="summarization", end_key=END)

        return self.graph_builder.compile()
