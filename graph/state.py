"""
Docstring for graph.state
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
from schema import (
    AnalysisOrchestration,
    ComputationPlanning,
    IntentComprehension,
    Observation,
    RequestClassification,
)

class State(MessagesState):
    """
    Docstring for State
    """
    ui_payload: Optional[Dict[str, str]]
    intent_comprehension: Optional[IntentComprehension]
    request_classification: Optional[RequestClassification]
    analysis_orchestration: Optional[AnalysisOrchestration]
    computation_planning: Optional[ComputationPlanning]
    execution: Optional[Execution]
    observation: Optional[Observation]
    summarization: Optional[AIMessage]
