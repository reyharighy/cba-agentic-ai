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
    Determination of conversational context relevance.
    """
    relevant_turns: List[str] = Field(
        ...,
        description="Ordered list of turn numbers that should be retrieved and inspected"
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation of why these turns were selected in English"
    )

class RequestClassification(BaseModel):
    """
    Routing decision for request handling.
    """
    route: Literal["analysis_orchestration", "direct_response", "punt_response"] = Field(
        ...,
        description="Route category that is selected based-on the current user's request"
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation of why this route category is selected in English"
    )

class AnalysisOrchestration(BaseModel):
    """
    Analytical execution planning and routing decision.
    """
    route: Literal["data_unavailability", "data_retrieval", "computation_planning"] = Field(
        ...,
        description="Route category that is selected based-on the current user's request"
    )
    sql_query: Optional[str] = Field(
        ...,
        description="SQL query to execute if data_retrieval is required for the next process"
    )
    syntax_rationale: str = Field(
        ...,
        description="Clear and detailed explanation of why the generated SQL query is valid and appropriate"
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation of why this route category is selected in English"
    )

class Step(BaseModel):
    """
    Single executable step in an analytical computation plan.
    """
    number: int = Field(
        ...,
        ge=1,
        description="Sequential step number, starting from 1"
    )
    description: str = Field(
        ...,
        description="What this step does in plain English"
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
        description="Python code in order to execute based on description step"
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation of why this step is necessary in English"
    )

class ComputationPlanning(BaseModel):
    """
    Executable analytical computation plan.
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
        description="Clear and detailed explanation of why this procedure satisfies the user's request in English"
    )

class Observation(BaseModel):
    """
    Evaluation of executable analytical computation plan results.
    """
    status: Literal["sufficient", "insufficient"] = Field(
        ...,
        description="Classification of whether the execution result satisfies the user's request or not"
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation of why the execution result sufficient or not to answer the user's request in English"
    )
    
