# internal
from .intent_comprehension import INTENT_COMPREHENSION
from .request_classification import REQUEST_CLASSIFICATION
from .context_distillation import CONTEXT_DISTILLATION
from .punt_response import PUNT_RESPONSE
from .analytical_requirement import ANALYTICAL_REQUIREMENT
from .direct_response import DIRECT_RESPONSE
from .data_availability import (
    DATA_AVAILABILITY,
    DATA_AVAILABILITY_FROM_DATA_RETRIEVAL_PLAN,
)
from .data_unavailability_response import DATA_UNAVAILABILITY_RESPONSE
from .data_retrieval_plan import (
    DATA_RETRIEVAL_PLAN,
    DATA_RETRIEVAL_PLAN_FROM_DATA_RETRIEVAL_PLAN_EXECUTION,
    DATA_RETRIEVAL_PLAN_FROM_DATA_RETRIEVAL_PLAN_OBSERVATION,
    DATA_RETRIEVAL_PLAN_OBSERVATION,
)
from .analytical_plan import (
    ANALYTICAL_PLAN,
    ANALYTICAL_PLAN_FROM_ANALYTICAL_PLAN_EXECUTION,
    ANALYTICAL_PLAN_FROM_ANALYTICAL_PLAN_OBSERVATION,
    ANALYTICAL_PLAN_OBSERVATION,
)
from .analytical_result import ANALYTICAL_RESULT
from .infographic_requirement import INFOGRAPHIC_REQUIREMENT
from .infographic_plan import (
    INFOGRAPHIC_PLAN,
    INFOGRAPHIC_PLAN_FROM_INFOGRAPHIC_PLAN_EXECUTION,
    INFOGRAPHIC_PLAN_FROM_INFOGRAPHIC_PLAN_OBSERVATION,
    INFOGRAPHIC_PLAN_OBSERVATION,
)
from .summarization import SUMMARIZATION

prompt_dict: dict[str, str] = {
    "__intent_comprehension": INTENT_COMPREHENSION,
    "__request_classification": REQUEST_CLASSIFICATION,
    "__context_distillation": CONTEXT_DISTILLATION,
    "__punt_response": PUNT_RESPONSE,
    "__analytical_requirement": ANALYTICAL_REQUIREMENT,
    "__direct_response": DIRECT_RESPONSE,
    "__data_availability": DATA_AVAILABILITY,
    "__data_availability_from_data_retrieval_plan": DATA_AVAILABILITY_FROM_DATA_RETRIEVAL_PLAN,
    "__data_unavailability_response": DATA_UNAVAILABILITY_RESPONSE,
    "__data_retrieval_plan": DATA_RETRIEVAL_PLAN,
    "__data_retrieval_plan_from_data_retrieval_plan_execution": DATA_RETRIEVAL_PLAN_FROM_DATA_RETRIEVAL_PLAN_EXECUTION,
    "__data_retrieval_plan_from_data_retrieval_plan_observation": DATA_RETRIEVAL_PLAN_FROM_DATA_RETRIEVAL_PLAN_OBSERVATION,
    "__data_retrieval_plan_observation": DATA_RETRIEVAL_PLAN_OBSERVATION,
    "__analytical_plan": ANALYTICAL_PLAN,
    "__analytical_plan_from_analytical_plan_execution": ANALYTICAL_PLAN_FROM_ANALYTICAL_PLAN_EXECUTION,
    "__analytical_plan_from_analytical_plan_observation": ANALYTICAL_PLAN_FROM_ANALYTICAL_PLAN_OBSERVATION,
    "__analytical_plan_observation": ANALYTICAL_PLAN_OBSERVATION,
    "__analytical_result": ANALYTICAL_RESULT,
    "__infographic_requirement": INFOGRAPHIC_REQUIREMENT,
    "__infographic_plan": INFOGRAPHIC_PLAN,
    "__infographic_plan_from_infographic_plan_execution": INFOGRAPHIC_PLAN_FROM_INFOGRAPHIC_PLAN_EXECUTION,
    "__infographic_plan_from_infographic_plan_observation": INFOGRAPHIC_PLAN_FROM_INFOGRAPHIC_PLAN_OBSERVATION,
    "__infographic_plan_observation": INFOGRAPHIC_PLAN_OBSERVATION,
    "__summarization": SUMMARIZATION,
}

__all__ = ["prompt_dict"]
