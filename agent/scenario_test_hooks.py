# standard
import os

# internal
from .state import State

_FORCED_DATA_RETRIEVAL_OBSERVATION_RATIONALE: str = (
    "[scenario test] Forced insufficient observation to verify retrieval correction loop."
)

_FORCED_DATA_RETRIEVAL_INTERRUPT_RATIONALE: str = (
    "[scenario test] Forced insufficient observation to exhaust retrieval retries and trigger interrupt."
)

_FORCED_ANALYTICAL_OBSERVATION_RATIONALE: str = (
    "[scenario test] Forced insufficient observation to verify analytical correction loop."
)


def _interrupt_harness_enabled() -> bool:
    return os.getenv("SCENARIO_TEST_FORCE_DATA_RETRIEVAL_INTERRUPT", "false").lower() == "true"


def _retrieval_retry_once_harness_enabled() -> bool:
    return os.getenv("SCENARIO_TEST_FORCE_DATA_RETRIEVAL_RETRY_ONCE", "false").lower() == "true"


def should_force_data_retrieval_observation_insufficient(
    state: State,
    *,
    max_correction_retries: int,
) -> bool:
    """
    Return True when the scenario test harness should force an insufficient
    retrieval observation before normal LLM evaluation runs.
    """
    if _interrupt_harness_enabled():
        if state.get("post_interrupt_resume"):
            return False

        return state["data_retrieval_retry_count"] < max_correction_retries

    if _retrieval_retry_once_harness_enabled():
        return state["data_retrieval_retry_count"] == 0

    return False


def force_data_retrieval_observation_retry_once(state: State) -> bool:
    """
    Return True when the S5 harness should force one retrieval observation retry.
    """
    return _retrieval_retry_once_harness_enabled() and state["data_retrieval_retry_count"] == 0


def forced_data_retrieval_observation_rationale(state: State | None = None) -> str:
    """
    Rationale recorded when the test harness forces an insufficient observation.
    """
    if _interrupt_harness_enabled() and state is not None:
        attempt: int = state["data_retrieval_retry_count"] + 1
        return f"{_FORCED_DATA_RETRIEVAL_INTERRUPT_RATIONALE} (attempt {attempt})"

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
