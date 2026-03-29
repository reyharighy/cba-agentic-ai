# pyright: reportMissingTypeStubs=false

# third-party
from e2b_code_interpreter import Execution
from langchain_core.messages import AIMessage, HumanMessage
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


def make_initial_state(user_input: str) -> "State":
    """
    Create an initial State object with the user's input.
    """
    return State(
        messages=[HumanMessage(content=user_input)],
        ui_payload=None,
        current_node=None,
        intent_comprehension=None,
        request_classification=None,
        analytical_requirement=None,
        context_distillation=None,
        data_availability=None,
        data_retrieval_plan=None,
        data_retrieval_plan_execution=None,
        data_retrieval_plan_observation=None,
        analytical_plan=None,
        analytical_plan_execution=None,
        analytical_plan_observation=None,
        analytical_result=None,
        infographic_requirement=None,
        infographic_plan=None,
        infographic_plan_execution=None,
        infographic_plan_observation=None,
        summarization=None,
    )


class State(MessagesState):
    """
    State object for the agent.
    """

    ui_payload: dict[str, str] | None
    current_node: str | None
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
