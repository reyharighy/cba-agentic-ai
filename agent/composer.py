"""
The composer is responsible for deriving and assembling contextual
information used by graph nodes before and after LLM inference.
It does not execute graph logic or control flow.

This module provides helper functions used by graph nodes to retrieve,
transform, and assemble contextual information.
"""
# standard
from typing import (
    List,
    Sequence,
)

# third-party
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)

# internal
from .state import State
from context.database import ContextManager
from memory.database import MemoryManager
from memory.models import (
    ChatHistory,
    ChatHistoryShow,
    ShortMemory
)

class Composer:
    def __init__(self, context_manager: ContextManager, memory_manager: MemoryManager) -> None:
        """
        Initialize the composer with access to contextual runtime.
        """
        self.context_manager: ContextManager = context_manager
        self.memory_manager: MemoryManager = memory_manager

    def get_conversation_summary(self) -> str:
        """
        Construct a summarized view of prior conversation turns.

        The summary is derived from short-term memory and formatted as
        prompt-ready context to provide historical grounding for
        downstream LLM reasoning.
        """
        short_memories: List[ShortMemory] = self.memory_manager.index_short_memory()

        if short_memories:
            context_prompt: str = "\n\nConversation history summarized by turn number:"

            for short_memory in short_memories:
                context_prompt += f"\n[TURN-{short_memory.turn_num}]: {short_memory.summary}"

            return context_prompt

        return "\n\nThere is no conversation history."

    def get_relevant_conversation(self, state: State) -> Sequence:
        """
        Assemble conversation turns relevant to the current request.

        Relevant turns are selected based on intent comprehension results
        stored in the agent state and reconstructed as role-preserving
        LangChain message objects suitable for LLM input.
        """
        llm_input: Sequence = []

        if state["intent_comprehension"]:
            for turn_num in state["intent_comprehension"].relevant_turns:
                params: ChatHistoryShow = ChatHistoryShow(turn_num=int(turn_num))
                relevant_turn: List[ChatHistory] = self.memory_manager.show_chat_history(params)

                for chat in relevant_turn:
                    if chat.role == "Human":
                        llm_input += [HumanMessage(content=chat.content)]
                    else:
                        llm_input += [AIMessage(content=chat.content)]

        return llm_input
