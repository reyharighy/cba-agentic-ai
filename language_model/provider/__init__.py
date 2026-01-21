"""
Language model definitions for the agentic system.

This module defines the LLMs used by the system. No matter the provider or
specification API, as long as a model exposes a BaseChatModel interface from
langchain_core, it can be plugged in and used interchangeably.
"""
from .groq import (
    groq_gpt_120b_low,
    groq_gpt_120b_medium,
    groq_gpt_120b_high,
)

__all__ = [
    "groq_gpt_120b_low",
    "groq_gpt_120b_medium",
    "groq_gpt_120b_high",
]
