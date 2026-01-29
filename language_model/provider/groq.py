"""
Chat model provided by Groq from langchain_core interface of BaseChatModel.
"""
# third-party
from langchain_core.language_models.chat_models import BaseChatModel
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
    model="meta-llama/llama-4-maverick-17b-128e-instruct",
    temperature=0,
    max_tokens=None,
    timeout=None
)
