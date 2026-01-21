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
)

groq_gpt_120b_medium: BaseChatModel = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    reasoning_effort="medium",
)

groq_gpt_120b_high: BaseChatModel = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    reasoning_effort="high",
)
