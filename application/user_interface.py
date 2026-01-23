"""
Streamlit-based user interface implementation.

This module defines the primary UI layer responsible for rendering chat
interactions, streaming graph execution output, and coordinating user input
with the orchestration graph.
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
from streamlit.delta_generator import DeltaGenerator
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

# internal
from .runtime import SessionMemory
from agent import (
    Context,
    State,
)
from agent.stages import (
    enable_interactive_graph,
    images_source_path,
)
from cache import (
    load_graph,
    load_prompts_set,
    load_sandbox_bootstrap,
)
from memory.database import MemoryManager
from memory.models import ChatHistory

class UserInterface:
    def __init__(self, memory_manager: MemoryManager) -> None:
        """
        Initialize the user interface with required persistence dependencies.

        The database manager is used exclusively for retrieving chat history.
        """
        self.session_memory: SessionMemory = SessionMemory()
        self.memory_manager: MemoryManager = memory_manager

    def run(self) -> None:
        """
        Entry point for rendering and running the user interface.
        """
        self._init_session_and_config()
        self._display_chat_history()
        self._process_chat_input()
        self._show_toast_message()

    def _init_session_and_config(self) -> None:
        """
        Initialize Streamlit session state and application configuration.
        """
        if st.session_state.get("init_app") is None:
            self.memory_manager.init_internal_database()
            st.session_state["success_toast"] = False
            st.session_state["error_toast"] = False
            st.session_state["punt_toast"] = False
            st.session_state["punt_response"] = []
            st.session_state["init_app"] = not None
            st.rerun()

        st.set_page_config(
            page_title="CBA - Agentic AI",
            layout="wide",
            initial_sidebar_state="auto"
        )

    def _display_chat_history(self) -> None:
        """
        Render persisted chat history into the UI.

        Chat turns are grouped and displayed sequentially to reflect prior
        interactions within the current session.
        """
        chat_history: List[ChatHistory] = self.memory_manager.index_chat_history()
        self.session_memory.turn_num = max(chat.turn_num for chat in chat_history) if chat_history else 0

        if self.session_memory.turn_num > 0:
            chat_turn_slicer: List[Union[ChatHistory, str]] = []

            for chat in chat_history:
                chat_turn_slicer.append(chat)

                if len(chat_turn_slicer) == 2:
                    self._render_chat_turn_block(chat_turn=chat_turn_slicer)
                    chat_turn_slicer = []

    def _process_chat_input(self) -> None:
        """
        Capture and process new user input.

        When a new prompt is submitted, the UI immediately renders the input
        and triggers a rerun after graph execution.
        """
        if chat_input := st.chat_input("Chat with AI"):
            self.session_memory.chat_input = chat_input
            self._render_chat_turn_block(on_processing_request=True)
            st.rerun()

    def _render_chat_turn_block(self, on_processing_request: bool = False, chat_turn: List[Union[ChatHistory, str]] = []) -> None:
        """
        Render a single chat turn block.

        A chat turn consists of a user prompt and a corresponding system response,
        optionally displaying streamed output during active processing.
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
        Render an individual element within a chat turn.

        Depending on the execution state, this method either displays persisted
        content or streams live output from the graph execution.
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
        Invoke the orchestration graph and stream execution updates to the UI.

        This method bridges user input to the compiled state graph, monitors
        node-level updates, and renders intermediate status and final outputs
        as they become available.
        """
        graph: CompiledStateGraph[State, Context] = load_graph()

        graph_input: State = State(
            messages=[HumanMessage(self.session_memory.chat_input)],
            ui_payload=None,
            next_node=None,
            intent_comprehension=None,
            request_classification=None,
            analytical_requirement=None,
            data_availability=None,
            data_retrival_planning=None,
            data_retrival_execution=None,
            data_retrival_observation=None,
            analytical_planning=None,
            analytical_plan_execution=None,
            analytical_observation=None,
            analytical_result=None,
            infograhic_requirement=None,
            infographic_planning=None,
            infographic_plan_execution=None,
            infographic_observation=None
        )

        graph_context: Context = Context(
            turn_num=self.session_memory.turn_num,
            prompts_set=load_prompts_set(),
            sandbox_bootstrap=load_sandbox_bootstrap()
        )

        end_nodes: List[str] = ["punt_response", "summarization"]
        pass_through_nodes: List[str] = ["data_retrieval", "sandbox_environment"]
        status_box: DeltaGenerator = st.status("Understanding request intent", expanded=True)
        column_containers: List[DeltaGenerator] = []
        graph_placeholder: Optional[DeltaGenerator] = None

        if enable_interactive_graph:
            column_containers = status_box.columns([0.4, 0.6], border=True)
            column_containers[0].subheader("Graph Execution Runtime Visualization")
            column_containers[1].subheader("Thinking Output")
            graph_placeholder = column_containers[0].empty()
            self._render_graph_element(graph_placeholder, None)

        try:
            for chunk in graph.stream(input=graph_input, context=graph_context, stream_mode="updates"):
                if not isinstance(chunk, Dict):
                    continue

                node_name, node_state = next(iter(chunk.items()))

                if not node_state or not isinstance(node_state, Dict):
                    continue

                if ui_payload := node_state.get("ui_payload"):
                    status_box.update(label=ui_payload)

                if node_name in pass_through_nodes:
                    action_output: str = "Extracted business data." if node_name == "data_retrieval" else "Executed computational plan."

                    if column_containers:
                        column_containers[1].write(action_output)
                    else:
                        status_box.write(action_output)

                    if enable_interactive_graph and graph_placeholder and node_name not in end_nodes:
                        self._render_graph_element(graph_placeholder, node_state)

                    continue

                try:
                    if node_name == "self_correction" or node_name == "self_reflection":
                        self.session_memory.thinking = node_state["computation_planning"].rationale
                    else:
                        self.session_memory.thinking = node_state[node_name].rationale

                    if enable_interactive_graph and graph_placeholder and node_name not in end_nodes:
                        column_containers[1].write(self._stream_generator)
                        self._render_graph_element(graph_placeholder, node_state)
                    else:
                        status_box.write(self._stream_generator)

                except Exception as _:
                    if node_name != "summarization":
                        self.session_memory.chat_output = node_state["messages"][-1].content
                        st.write(self._stream_generator)

                        if enable_interactive_graph and graph_placeholder and node_name != "punt_response" and node_state["next_node"] == "summarization":
                            self._render_graph_element(graph_placeholder, node_state)

                    if node_name == "summarization":
                        st.session_state["success_toast"] = True
                    elif node_name == "punt_response":
                        st.session_state["punt_toast"] = True
                        st.session_state["punt_response"].append(self.session_memory.chat_input)
                        st.session_state["punt_response"].append(self.session_memory.chat_output)
                        status_box.update(state="complete")

        except Exception as e:
            st.session_state["error_toast"] = True
            st.error(f"Graph execution failed: {e}")

    def _render_graph_element(self, graph_placeholder: DeltaGenerator, node_state: Optional[Dict]) -> None:
        """
        Render the current execution stage of the orchestration graph.

        This method updates the graph visualization in the UI by displaying
        a static image corresponding to the graph's next node. When no node
        state is available, it renders the initial entry point of the graph.
        """
        graph_placeholder.image(
            image=f"{images_source_path}/{node_state["next_node"]}.png" if node_state else f'{images_source_path}/intent_comprehension.png',
            width="stretch",
        )

    def _stream_generator(self) -> Generator:
        """
        Generate streamed text output for incremental rendering.

        This generator yields tokens derived from either intermediate reasoning
        or final chat output, enabling a progressive display experience.
        """
        if self.session_memory.thinking:
            for word in str(self.session_memory.thinking).split(" "):
                yield word + " "
                sleep(0.01)

            self.session_memory.thinking = None

        elif self.session_memory.chat_output:
            for word in str(self.session_memory.chat_output).split(" "):
                yield word + " "
                sleep(0.01)

    def _show_toast_message(self) -> None:
        """
        Display contextual toast notifications to the user.

        Notifications reflect execution outcomes such as success, domain mismatch,
        or system failure.
        """
        if st.session_state["success_toast"]:
            st.session_state["success_toast"] = False

            st.toast(
                body="###### **Your request is completed.**", 
                duration="long"
            )

        if st.session_state["punt_toast"]:
            self._render_chat_turn_block(chat_turn=st.session_state["punt_response"])
            st.session_state["punt_toast"] = False
            st.session_state["punt_response"] = []

            st.toast(
                body="###### **Your request is out of business analytics domain. This chat turn will not be persisted.**", 
                duration="long"
            )

        if st.session_state["error_toast"]:
            st.session_state["error_toast"] = False

            st.toast(
                body="###### **System fails to process your request. Please try again.**", 
                duration="long"
            )
