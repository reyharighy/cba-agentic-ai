# pyright: reportMissingTypeStubs=false

# third-party
from e2b_code_interpreter import Execution
from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState

# internal
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


class State(MessagesState):
    """
    State class for managing the graph state during the transition of nodes.

    This class extends MessagesState to include specific attributes relevant to the analytical and infographic generation process.
    """

    ui_payload: dict[str, str] | None
    next_node: str | None
    intent_comprehension: IntentComprehension | None
    request_classification: RequestClassification | None
    analytical_requirement: AnalyticalRequirement | None
    context_distillation: AIMessage | None
    data_availability: DataAvailability | None
    data_retrieval_plan: DataRetrievalPlan | None
    data_retrieval_plan_execution: ValueError | None
    data_retrieval_plan_observation: DataRetrievalPlanObservation | None
    analytical_plan: AnalyticalPlan | None
    analytical_plan_execution: Execution | None
    analytical_plan_observation: AnalyticalPlanObservation | None
    analytical_result: AIMessage | None
    infographic_requirement: InfographicRequirement | None
    infographic_plan: InfographicPlan | None
    infographic_plan_execution: Execution | None
    infographic_plan_observation: InfographicPlanObservation | None
    summarization: AIMessage | None
