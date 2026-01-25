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
    Captures which prior conversation turns are required to understand or fulfill the current user request.
    """
    relevant_turns: List[str] = Field(
        ...,
        description="Ordered list of turn numbers that should be retrieved and inspected in order to help answering the user's request"
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English"
    )

class RequestClassification(BaseModel):
    """
    Represents the result of classifying whether a user request falls within the business analytics domain.
    """
    request_is_business_analytical_domain: bool = Field(
        ...,
        description=(
            "The value must be set to True if the user's request is within business analytical domain. "
            "Otherwise, set the value to False."
        )
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English"
    )

class AnalyticalRequirement(BaseModel):
    """
    Represents a decision contract that determines whether answering the user's request requires an analytical process.
    """
    analytical_process_is_required: bool = Field(
        ...,
        description=(
            "The value must be set to True if the user's request requires analytical process to the answer the user's request. "
            "Otherwise, set the value to False."
        )
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English"
    )

class DataAvailability(BaseModel):
    """
    Indicates whether the required business data exists in the external database to support analytical processing for the user's request.
    """
    data_is_available: bool = Field(
        ...,
        description=(
            "The value must be set to True if the data is available in external database in order to answer the user's request"
            "Otherwise, set the value to False."
        )
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English"
    )

class DataRetrievalPlanning(BaseModel):
    """
    Defines a data extraction plan by generating a SQL query that retrieves raw data from an external database into an analytical workspace.
    """
    sql_query: Optional[str] = Field(
        ...,
        description="The SQL Query to execute on external database in order to extract and prepare data into dataframe before analytical execution"
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English"
    )

class DataRetrievalObservation(BaseModel):
    """
    Represents an evaluation of whether retrieved raw data is sufficient to support the intended downstream analytical process.
    """
    result_is_sufficient: bool = Field(
        ...,
        description=(
            "The value must be set to True if the execution result fulfils the data retrieval planning. "
            "Otherwise, set the value to False."
        )
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English"
    )

class AnalyticalStep(BaseModel):
    """
    Each step defines how data should be transformed or processed programmatically, without executing the operation or interpreting the result.
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
        description="Name of the input dataframe variable"
    )
    output_df: str = Field(
        ...,
        description="Name of the output dataframe variable"
    )
    python_code: str = Field(
        ...,
        description="Python code in order to execute based on description step"
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English"
    )

class AnalyticalPlanning(BaseModel):
    """
    This plan specifies the analysis type and an ordered sequence of computational steps that can be executed later in a controlled sandbox environment.
    """
    analysis_type: Literal["descriptive", "diagnostic", "predictive", "inferential"] = Field(
        ...,
        description="Analysis type to take in order to answer the user's request"
    )
    plan: List[AnalyticalStep] = Field(
        ...,
        description="Ordered list of analytical steps to take in order to answer the user's request"
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English"
    )

class AnalyticalPlanObservation(BaseModel):
    """
    Represents an evaluation of whether analytical execution results sufficiently fulfil the analytical plan and support answering the user's business analytical request.
    """
    result_is_sufficient: bool = Field(
        ...,
        description=(
            "The value must be set to True if the execution result fulfils the analytical planning. "
            "Otherwise, set the value to False."
        )
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English"
    )

class InfographicRequirement(BaseModel):
    """
    Docstring for InfographicRequirement
    """
    infographic_is_required: bool = Field(
        ...,
        description=(
            "The value must be set to True if the infographics is required to enhance the analytical results. "
            "Otherwise, set the value to False."
        )
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English"
    )

class InfographicStep(BaseModel):
    """
    Docstring for Plot
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
        description="Name of the input dataframe variable"
    )
    output_graph_path: str = Field(
        ...,
        description="Path where the output graph is saved"
    )
    python_code: str = Field(
        ...,
        description="Python code in order to execute based on description step"
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English"
    )

class InfographicPlanning(BaseModel):
    """
    Docstring for InfographicPlanning
    """
    plan: List[InfographicStep] = Field(
        ...,
        description="Ordered list of infographic steps to take in order to enhance the analytical results"
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English"
    )

class InfographicObservation(BaseModel):
    """
    Docstring for InfographicObservation
    """
    result_is_sufficient: bool = Field(
        ...,
        description=(
            "The value must be set to True if the execution result fulfils the infographic planning. "
            "Otherwise, set the value to False."
        )
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English"
    )
