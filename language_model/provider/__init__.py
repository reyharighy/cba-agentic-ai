"""
Language model definitions for the agentic system.

This module defines the LLMs used by the system. No matter the provider or
specification API, as long as a model exposes a BaseChatModel interface from
langchain_core, it can be plugged in and used interchangeably.
"""
from .groq import (
    groq_gpt_120b,
    groq_kimi_k2,
)

__all__ = [
    "groq_gpt_120b",
    "groq_kimi_k2",
]
