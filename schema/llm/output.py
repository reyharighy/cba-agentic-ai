"""
Output schemas for LLM-driven node execution.

This module defines structured output formats that language models
must conform to when producing results for specific system nodes.
These schemas act as strict interfaces between probabilistic model
generation and deterministic system logic.
"""
# standard
from typing import (
    Literal,
    List,
    Optional,
)

# third-party
from pydantic import (
    BaseModel,
    Field,
)

class IntentComprehension(BaseModel):
    """
    Identify which conversation turns are relevant for downstream reasoning.
    """
    relevant_turns: List[str] = Field(
        ...,
        description="Ordered list of turn numbers that should be retrieved and inspected"
    )
    rationale: str = Field(
        ...,
        description="Short explanation of why these turns were selected"
    )

class RequestClassification(BaseModel):
    """
    Identify which route category is relevant for the next process.
    """
    route: Literal["analysis_orchestration", "direct_response", "punt_response"] = Field(
        ...,
        description="Route category that is selected based-on the current user's request"
    )
    rationale: str = Field(
        ...,
        description="Short explanation of why this route category is selected"
    )

class AnalysisOrchestration(BaseModel):
    """
    Identify which route category is relevant for the next process.
    """
    route: Literal["data_unavailability", "data_retrieval", "computation_planning"] = Field(
        ...,
        description="Route category that is selected based-on the current user's request"
    )
    sql_query: Optional[str] = Field(
        ...,
        description="SQL query to execute if data_retrieval is required for the next process"
    )
    rationale: str = Field(
        ...,
        description="Short explanation of why this route category is selected"
    )

class Step(BaseModel):
    """
    Step item should be taken in a computation planning.
    """
    number: int = Field(
        ...,
        ge=1,
        description="Sequential step number, starting from 1"
    )
    description: str = Field(
        ...,
        description="What this step does in plain language. Use English"
    )
    input_df: Optional[str] = Field(
        ...,
        description="Name of the input dataframe variable (e.g. df)"
    )
    output_df: str = Field(
        ...,
        description="Name of the output dataframe variable (e.g. df_filtered)"
    )
    python_code: str = Field(
        ...,
        description="Python code in order to execute based-on description step"
    )
    rationale: str = Field(
        ...,
        description="Short explanation of why this step is necessary"
    )

class ComputationPlanning(BaseModel):
    """
    List of steps that should be taken in order to answer the user's request.
    """
    analysis_type: Literal["descriptive", "diagnostic", "predictive", "inferential"] = Field(
        ...,
        description="Analysis type based on the current user's request"
    )
    steps: List[Step] = Field(
        ...,
        description="Ordered list of computation steps"
    )
    rationale: str = Field(
        ...,
        description="Why this procedure satisfies the user's request"
    )

class Observation(BaseModel):
    """
    Docstring for Observation
    """
    status: Literal["sufficient", "insufficient"] = Field(
        ...,
        description="Classification of whether the execution result satisfies the user's request or not"
    )
    rationale: str = Field(
        ...,
        description="Clear, concise explanation of why the execution result is or is not sufficient to answer the user's request"
    )
    
