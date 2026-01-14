"""
Docstring for graph.state
"""
# standard
from typing import Optional

# third-party
from e2b_code_interpreter import Execution
from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState
from pandas import DataFrame

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
    intent_comprehension: Optional[IntentComprehension]
    request_classification: Optional[RequestClassification]
    dataframe: Optional[DataFrame]
    analysis_orchestration: Optional[AnalysisOrchestration]
    computation_planning: Optional[ComputationPlanning]
    execution: Optional[Execution]
    observation: Optional[Observation]
    summarization: Optional[AIMessage]
