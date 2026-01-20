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
    groq_gpt_120b,
    groq_kimi_k2,
)
from util import st_cache

@st_cache("Loading language models", "resource")
def load_language_models() -> Dict[Literal["complex", "basic"], BaseChatModel]:
    """
    Load the language model instances.

    This function provides access to the language models used by
    the agent when inferencing the input. It provides two specification
    models divided based on complexity task each node processes.
    """
    return {
        "complex": groq_gpt_120b,
        "basic": groq_kimi_k2
    }
