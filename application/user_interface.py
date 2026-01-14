"""
Docstring for application.user_interface
"""
# standard
from time import sleep
from typing import (
    Dict,
    Generator,
    List,
    Optional,
    Union,
)

# third-party
import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

# internal
from .runtime import SessionMemory
from cache import (
    load_graph_orchestrator,
    load_prompts_set,
    load_sandbox_bootstrap,
)
from context import (
    ChatHistory,
    DatabaseManager,
)
from graph import (
    Context,
    State,
)

class UserInterface:
    """
    Docstring for UserInterface
    
    :var Returns: Description
    """
    def __init__(self) -> None:
        """
        Docstring for __init__
        
        :param self: Description
        """
        self.session_memory: SessionMemory = SessionMemory()
        self.db_manager: DatabaseManager = DatabaseManager()

    def run(self) -> None:
        """
        Docstring for run
        
        :param self: Description
        """
        self._init_session_state_and_page_config()
        self._display_chat_history()
        self._process_chat_input()
        self._show_toast_message()

    def _init_session_state_and_page_config(self) -> None:
        """
        Docstring for init_session
        
        :param self: Description
        """
        if st.session_state.get("init_app") is None:
            self.db_manager.init_internal_database()
            st.session_state["success_message"] = False
            st.session_state["error_message"] = False
            st.session_state["punt_response"] = False
            st.session_state["last_punt_response"] = []
            st.session_state["init_app"] = not None
            st.rerun()

        st.set_page_config(
            page_title="CBA - Agentic AI",
            layout="wide",
            initial_sidebar_state="auto"
        )

    def _display_chat_history(self) -> None:
        """
        Docstring for display_chat_history
        
        :param self: Description
        """
        chat_history: List[ChatHistory] = self.db_manager.index_chat_history()
        self.session_memory.turn_num = len(chat_history)

        if self.session_memory.turn_num > 0:
            chat_turn_slicer: List[Union[ChatHistory, str]] = []

            for chat in chat_history:
                chat_turn_slicer.append(chat)

                if len(chat_turn_slicer) == 2:
                    self._render_chat_turn_block(chat_turn=chat_turn_slicer)
                    chat_turn_slicer = []

    def _process_chat_input(self) -> None:
        """
        Docstring for process_chat_input
        
        :param self: Description
        """
        if chat_input := st.chat_input("Chat with AI"):
            self.session_memory.chat_input = chat_input

            try:
                self._render_chat_turn_block(on_processing_request=True)
            except Exception as e:
                st.error(e)
                st.session_state["error_message"] = True

            st.rerun()

    def _render_chat_turn_block(self, on_processing_request: bool = False, chat_turn: List[Union[ChatHistory, str]] = []) -> None:
        """
        Docstring for _render_chat_turn_block
        
        :param self: Description
        :param on_processing_request: Description
        :type on_processing_request: bool
        :param chat_turn: Description
        :type chat_turn: List[Union[ChatHistory, str]]
        """
        st.divider()

        with st.expander('Click to toggle cell', expanded=True):
            with st.container(border=True):
                st.badge('Your Prompt', color='orange')

                self._render_turn_element(
                    input_type=True,
                    on_processing_request=on_processing_request,
                    turn_element=chat_turn[0] if not on_processing_request else None
                )

            st.badge('System Response', color='blue')

            self._render_turn_element(
                input_type=False,
                on_processing_request=on_processing_request,
                turn_element=chat_turn[1] if not on_processing_request else None
            )
    
    def _render_turn_element(self, input_type: bool, on_processing_request: bool, turn_element: Optional[Union[ChatHistory, str]]) -> None:
        """
        Docstring for _render_turn_element
        
        :param self: Description
        :param element_type: Description
        :type element_type: Literal["input", "output"]
        :param on_processing_request: Description
        :type on_processing_request: bool
        :param turn_element: Description
        :type turn_element: Optional[Union[ChatHistory, str]]
        """
        if on_processing_request:
            st.write(self.session_memory.chat_input) if input_type else self._graph_invocation()
        elif isinstance(turn_element, ChatHistory):
            st.write(turn_element.content)
        elif isinstance(turn_element, str):
            st.write(turn_element)
        else:
            raise ValueError("'turn_element' must not be None when 'on_processing_request' is False")

    def _graph_invocation(self) -> None:
        """
        Docstring for graph_invocation
        
        :param self: Description
        """
        graph: CompiledStateGraph[State, Context] = load_graph_orchestrator()

        graph_input: State = State(
            messages=[HumanMessage(self.session_memory.chat_input)],
            intent_comprehension=None,
            request_classification=None,
            dataframe=self.db_manager.get_working_dataframe(),
            analysis_orchestration=None,
            computation_planning=None,
            execution=None,
            observation=None,
            summarization=None
        )

        graph_context: Context = Context(
            turn_num=self.session_memory.turn_num,
            prompts_set=load_prompts_set(),
            short_memories=self.db_manager.index_short_memory(),
            external_db_info=self.db_manager.inspect_external_database(),
            sandbox_bootstrap=load_sandbox_bootstrap()
        )

        graph_output: Dict = graph.invoke(
            input=graph_input,
            context=graph_context,
        )

        self.session_memory.chat_output = graph_output["messages"][-1].content

        if graph_output["summarization"]:
            st.session_state["success_message"] = True
        else:
            st.session_state["punt_response"] = True
            st.session_state["last_punt_response"].append(self.session_memory.chat_input)
            st.session_state["last_punt_response"].append(self.session_memory.chat_output)

        st.write_stream(self._stream_generator)

    def _stream_generator(self) -> Generator:
        """
        Docstring for stream_generator
        
        :param self: Description
        :return: Description
        :rtype: Generator[Any, None, None]
        """
        if self.session_memory.chat_output:
            for word in str(self.session_memory.chat_output).split(" "):
                yield word + " "
                sleep(0.02)

    def _show_toast_message(self) -> None:
        """
        Docstring for show_toast_message
        
        :param self: Description
        """
        if st.session_state["success_message"]:
            st.session_state["success_message"] = False

            st.toast(
                body="###### **Your request is completed.**", 
                duration="long"
            )

        if st.session_state["punt_response"]:
            st.session_state["punt_response"] = False
            self._render_chat_turn_block(chat_turn=st.session_state["last_punt_response"])

            st.toast(
                body="###### **Your request is out of business analytics domain. This chat turn will not be persisted.**", 
                duration="long"
            )

        if st.session_state["error_message"]:
            st.session_state["error_message"] = False

            st.toast(
                body="###### **System fails to process your request. Please try again.**", 
                duration="long"
            )
