# standard
from typing import Literal

# third-party
from pydantic import (
    BaseModel,
    Field,
)


class IntentComprehension(BaseModel):
    """
    Represents the identification of relevant conversational turns that provide necessary context to accurately understand
    and address the user's request.
    """

    relevant_turns: list[str] = Field(
        ...,
        description="List of relevant conversational turns that provide necessary context to understand the user's request",
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English",
    )


class RequestClassification(BaseModel):
    """
    Represents a decision contract that determines whether the user's request falls within the business analytical domain.
    """

    request_is_business_analytical_domain: bool = Field(
        ...,
        description=(
            "The value must be set to True if the user's request is within the business analytical domain. "
            "Otherwise, set the value to False."
        ),
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English",
    )


class AnalyticalRequirement(BaseModel):
    """
    Represents a decision on whether analytical process is required to answer the user's business analytical request.
    """

    analytical_process_is_required: bool = Field(
        ...,
        description=(
            "The value must be set to True if the analytical process is required to answer the user's request. "
            "Otherwise, set the value to False."
        ),
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English",
    )


class DataAvailability(BaseModel):
    """
    Represents a decision on whether the required data is available in an external database to support the analytical process.
    """

    data_is_available: bool = Field(
        ...,
        description=(
            "The value must be set to True if the required data is available in an external database. "
            "Otherwise, set the value to False."
        ),
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English",
    )


class DataRetrievalPlan(BaseModel):
    """
    Specifies a structured plan to extract and prepare data from an external database into a dataframe before the analytical
    execution.
    """

    sql_query: str = Field(
        ...,
        description="SQL query to retrieve the required data from the external database",
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English",
    )


class DataRetrievalPlanObservation(BaseModel):
    """
    Represents an evaluation of whether data retrieval execution results sufficiently fulfil the data retrieval plan.
    """

    result_is_sufficient: bool = Field(
        ...,
        description=(
            "The value must be set to True if the execution result fulfils the data retrieval plan. "
            "Otherwise, set the value to False."
        ),
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English",
    )


class AnalyticalStep(BaseModel):
    """
    Represents a single computational step within an analytical plan.
    """

    number: int = Field(
        ...,
        ge=1,
        description="Sequential number of the analytical step",
    )
    input_df: str = Field(
        ...,
        description="Name of the input dataframe variable",
    )
    output_df: str = Field(
        ...,
        description="Name of the output dataframe variable",
    )
    python_code: str = Field(
        ...,
        description="Python code to execute for this analytical step",
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English",
    )


class AnalyticalPlan(BaseModel):
    """
    Specifies a structured analytical plan to answer the user's business analytical request.
    """

    analysis_type: Literal[
        "descriptive",
        "diagnostic",
        "predictive",
        "inferential",
    ] = Field(
        ...,
        description="The type of analysis to be performed to answer the user's request",
    )
    plan: list[AnalyticalStep] = Field(
        ...,
        description="List of analytical steps to be executed sequentially",
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English",
    )


class AnalyticalPlanObservation(BaseModel):
    """
    Evaluate whether the analytical execution results sufficiently fulfil the analytical plan.
    """

    result_is_sufficient: bool = Field(
        ...,
        description=(
            "The value must be set to True if the execution result fulfils the analytical plan. "
            "Otherwise, set the value to False."
        ),
    )
    rationale: str = Field(
        ...,
        description="Clear and detailed explanation in English",
    )
