# third-party
from langchain_core.language_models.chat_models import (
    BaseChatModel,
)
from langchain_groq import ChatGroq

groq_gpt_120b_low: BaseChatModel = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    reasoning_effort="low",
    timeout=None,
)

groq_gpt_120b_medium: BaseChatModel = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    reasoning_effort="medium",
    timeout=None,
)

groq_gpt_120b_high: BaseChatModel = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    reasoning_effort="high",
    timeout=None,
)

groq_qwen: BaseChatModel = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0,
    max_tokens=None,
    timeout=None,
)
