"""
Cache utilities for language model resources.

This module provides cached access to language models used by the agent.
"""
# standard
from typing import (
    Dict,
    Literal,
)

# third-party
from langchain_core.language_models import BaseChatModel

# internal
from language_model.provider import (
    groq_gpt_120b_low,
    groq_gpt_120b_medium,
    groq_gpt_120b_high,
)
from util import st_cache

@st_cache("Loading language models", "resource")
def load_language_models() -> Dict[Literal["low", "medium", "high"], BaseChatModel]:
    """
    Load the language model instances.

    This function provides access to the language models used by
    the agent when inferencing the input. It provides two specification
    models divided based on complexity task each node processes.
    """
    return {
        "low": groq_gpt_120b_low,
        "medium": groq_gpt_120b_medium,
        "high": groq_gpt_120b_high,
    }
