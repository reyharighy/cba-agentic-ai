# standard
import os

# internal
from .state import State

_FORCED_DATA_RETRIEVAL_OBSERVATION_RATIONALE: str = (
    "[scenario test] Forced insufficient observation to verify retrieval correction loop."
)

_FORCED_ANALYTICAL_OBSERVATION_RATIONALE: str = (
    "[scenario test] Forced insufficient observation to verify analytical correction loop."
)


def force_data_retrieval_observation_retry_once(state: State) -> bool:
    """
    Return True when the scenario test harness should force one retrieval
    observation retry (observation → plan) before normal LLM evaluation resumes.
    """
    return (
        os.getenv("SCENARIO_TEST_FORCE_DATA_RETRIEVAL_RETRY_ONCE", "false").lower() == "true"
        and state["data_retrieval_retry_count"] == 0
    )


def forced_data_retrieval_observation_rationale() -> str:
    """
    Rationale recorded when the test harness forces an insufficient observation.
    """
    return _FORCED_DATA_RETRIEVAL_OBSERVATION_RATIONALE


def force_analytical_observation_retry_once(state: State) -> bool:
    """
    Return True when the scenario test harness should force one analytical
    observation retry (observation → plan) before normal LLM evaluation resumes.
    """
    return (
        os.getenv("SCENARIO_TEST_FORCE_ANALYTICAL_RETRY_ONCE", "false").lower() == "true"
        and state["analytical_retry_count"] == 0
    )


def forced_analytical_observation_rationale() -> str:
    """
    Rationale recorded when the test harness forces an insufficient analytical observation.
    """
    return _FORCED_ANALYTICAL_OBSERVATION_RATIONALE
