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
from schema.llm import (
    AnalysisOrchestration,
    ComputationPlanning,
    IntentComprehension,
    Observation,
    RequestClassification,
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
    intent_comprehension: Optional[IntentComprehension]
    request_classification: Optional[RequestClassification]
    analysis_orchestration: Optional[AnalysisOrchestration]
    computation_planning: Optional[ComputationPlanning]
    execution: Optional[Execution]
    observation: Optional[Observation]
    summarization: Optional[AIMessage]
