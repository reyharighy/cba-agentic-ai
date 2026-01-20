"""
Docstring for cache.language_model
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
    Docstring for load_language_models
    
    :return: Description
    :rtype: Dict[Literal['complex', 'basic'], BaseChatModel]
    """
    return {
        "complex": groq_gpt_120b,
        "basic": groq_kimi_k2
    }
