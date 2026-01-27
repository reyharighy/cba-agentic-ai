"""
State definitions for graph-based execution.

This module defines the mutable state object that flows through the graph.
The state is progressively enriched by node outputs and is used to
coordinate decision-making, execution routing, and response generation.
"""
# standard
from typing import (
    Dict,
    Optional,
)

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
    DataRetrievalPlanning,
    DataRetrievalObservation,
    AnalyticalPlanning,
    AnalyticalPlanObservation,
    InfographicRequirement,
    InfographicPlanning,
    InfographicPlanObservation
)

class State(MessagesState):
    """
    Mutable execution state propagated through the graph.

    This class represents the evolving analytical and conversational
    state during graph execution. Each node may read from and update
    specific fields to reflect its output, enabling downstream routing
    and decision logic.
    """
    ui_payload: Optional[Dict[str, str]]
    next_node: Optional[str]
    intent_comprehension: Optional[IntentComprehension]
    request_classification: Optional[RequestClassification]
    analytical_requirement: Optional[AnalyticalRequirement]
    data_availability: Optional[DataAvailability]
    data_retrieval_planning: Optional[DataRetrievalPlanning]
    data_retrieval_execution: Optional[ValueError]
    data_retrieval_observation: Optional[DataRetrievalObservation]
    analytical_planning: Optional[AnalyticalPlanning]
    analytical_plan_execution: Optional[Execution]
    analytical_plan_observation: Optional[AnalyticalPlanObservation]
    analytical_result: Optional[AIMessage]
    infographic_requirement: Optional[InfographicRequirement]
    infographic_planning: Optional[InfographicPlanning]
    infographic_plan_execution: Optional[Execution]
    infographic_plan_observation: Optional[InfographicPlanObservation]
