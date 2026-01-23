"""
The composer is responsible for deriving and assembling contextual
information used by graph nodes before and after LLM inference.
It does not execute graph logic or control flow.

This module provides helper functions used by graph nodes to retrieve,
transform, and assemble contextual information.
"""
# standard
import sys
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

    def get_conversation_summary_list(self) -> str:
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

    def get_punt_response_rationale(self, state: State) -> str:
        """
        Provide rationale to punt_response node.

        The rational is a base for the node to response produced by request_classification
        node in the previous process. Thus, it will help the response generated to be less
        template.
        """
        if state["request_classification"]:
            context_prompt: str = "\n\nThe rationale of why the user's request is not related to business analytics domain:\n"
            context_prompt += state["request_classification"].rationale

            return context_prompt

        raise ValueError(f"'request_classification' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")

    def get_database_schema_info(self) -> str:
        """
        Expose external database schema information.

        This context is used to inform analytical planning and query generation
        by describing available tables, columns, and structural metadata.
        """
        context_prompt: str = "\n\nThe external database schema information:\n"
        context_prompt += repr(self.context_manager.inspect_external_database())

        return context_prompt

    def get_data_unavailability_response_rationale(self, state: State) -> str:
        """
        Provide rationale to data_unavailability_response node.

        The rational is a base for the node to response produced by data_availability
        node in the previous process. Thus, it will help the response generated to be align 
        with contextual information of why the request can't be answered based on data
        """
        if state["data_availability"]:
            context_prompt: str = "\n\nThe rationale of why the external database is unsupported to answer the user's request:\n"
            context_prompt += state["data_availability"].rationale

            return context_prompt

        raise ValueError(f"'data_availability' state must not be empty in '{sys._getframe(1).f_code.co_name}' node")
