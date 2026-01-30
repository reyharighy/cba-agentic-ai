# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false

# standard
from collections.abc import Generator
from pathlib import Path
from time import sleep
from typing import Any

# third-party
import streamlit as st
from streamlit.delta_generator import (
    DeltaGenerator,
)
from langchain_core.messages import HumanMessage
from langgraph.graph.state import (
    CompiledStateGraph,
)

# internal
from .cache import (
    load_graph,
    load_prompts_set,
    load_analytical_sandbox_bootstrap,
    load_infographic_sandbox_bootstrap,
    load_infographic,
)
from .runtime import SessionMemory
from agent import (
    Context,
    State,
)
from agent.stages import (
    enable_interactive_graph,
    images_source_path,
)
from memory.database import MemoryManager
from memory.infographic import (
    infographic_dir_path,
)
from memory.models import ChatHistory


class UserInterface:
    def __init__(self, memory_manager: MemoryManager) -> None:
        """
        Initializes the UserInterface with the provided MemoryManager.
        """
        self.session_memory: SessionMemory = SessionMemory()
        self.memory_manager: MemoryManager = memory_manager

    def run(self) -> None:
        """
        Runs the user interface, handling session initialization, chat history display, chat input processing, and toast
        messages.
        """
        self.__init_session_and_config()
        self.__display_chat_history()
        self.__process_chat_input()
        self.__show_toast_message()

    def __init_session_and_config(self) -> None:
        """
        Initializes the session state and configures the Streamlit page.
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
            initial_sidebar_state="auto",
        )

    def __display_chat_history(self) -> None:
        """
        Displays the chat history from the memory manager.
        """
        chat_history: list[ChatHistory] = self.memory_manager.index_chat_history()
        self.session_memory.turn_num = max(chat.turn_num for chat in chat_history) if chat_history else 0

        if self.session_memory.turn_num > 0:
            message_block: list[ChatHistory | str] = []

            for chat in chat_history:
                message_block.append(chat)

                if len(message_block) == 2:
                    self.__render_chat_turn_block(chat_turn=message_block)
                    message_block = []

    def __process_chat_input(self) -> None:
        """
        Processes user chat input and triggers graph invocation.
        """
        if chat_input := st.chat_input("Chat with AI"):
            self.session_memory.chat_input = chat_input
            self.__render_chat_turn_block(on_processing_request=True)
            st.rerun()

    def __render_chat_turn_block(
        self, on_processing_request: bool = False, chat_turn: list[ChatHistory | str] = []
    ) -> None:
        """
        Renders a chat turn block in the user interface.
        """
        st.divider()

        with st.expander("Click to toggle cell", expanded=True):
            with st.container(border=True):
                st.badge("Your Prompt", color="orange")

                self.__render_turn_element(
                    input_type=True,
                    on_processing_request=on_processing_request,
                    turn_element=chat_turn[0] if not on_processing_request else None,
                )

            st.badge("System Response", color="blue")

            self.__render_turn_element(
                input_type=False,
                on_processing_request=on_processing_request,
                turn_element=chat_turn[1] if not on_processing_request else None,
            )

            if chat_turn and isinstance(chat_turn[-1], ChatHistory):
                self.__render_infographic_turn_block(chat_turn[-1].turn_num)

    def __render_turn_element(
        self, input_type: bool, on_processing_request: bool, turn_element: ChatHistory | str | None
    ) -> None:
        """
        Renders a turn element in the user interface.
        """
        if on_processing_request:
            st.write(self.session_memory.chat_input) if input_type else self.__graph_invocation()
        elif isinstance(turn_element, ChatHistory):
            st.write(turn_element.content)
        elif isinstance(turn_element, str):
            st.write(turn_element)
        else:
            raise ValueError("'turn_element' must not be None when 'on_processing_request' is False")

    def __render_infographic_turn_block(self, turn_num: int) -> None:
        """
        Renders the infographic turn block for the specified turn number.
        """
        infographic_object_dir_path: Path = infographic_dir_path / f"turn_num_{turn_num}"

        if infographic_object_dir_path.exists():
            infographic_object_file_path: Path = infographic_object_dir_path / "infographic.py"
            loader, module = load_infographic(infographic_object_file_path)

            if loader and module:
                loader.exec_module(module)

    def __graph_invocation(self) -> None:
        """
        Invokes the state graph and streams the output to the user interface.
        """
        graph: CompiledStateGraph[State, Context] = load_graph()

        graph_input: State = State(
            messages=[HumanMessage(self.session_memory.chat_input)],
            ui_payload=None,
            next_node=None,
            intent_comprehension=None,
            request_classification=None,
            analytical_requirement=None,
            context_distillation=None,
            data_availability=None,
            data_retrieval_plan=None,
            data_retrieval_plan_execution=None,
            data_retrieval_plan_observation=None,
            analytical_plan=None,
            analytical_plan_execution=None,
            analytical_plan_observation=None,
            analytical_result=None,
            infographic_requirement=None,
            infographic_plan=None,
            infographic_plan_execution=None,
            infographic_plan_observation=None,
            summarization=None,
        )

        graph_context: Context = Context(
            turn_num=self.session_memory.turn_num,
            prompts_set=load_prompts_set(),
            analytical_sandbox_bootstrap=load_analytical_sandbox_bootstrap(),
            infographic_sandbox_bootstrap=load_infographic_sandbox_bootstrap(),
        )

        status_box: DeltaGenerator = st.status(label="Understanding request intent", expanded=True)

        column_containers: list[DeltaGenerator] = []
        graph_placeholder: DeltaGenerator | None = None

        if enable_interactive_graph:
            column_containers = status_box.columns([0.4, 0.6], border=True)
            column_containers[0].subheader("Graph Execution Runtime Visualization")
            column_containers[1].subheader("Thinking Output")
            graph_placeholder = column_containers[0].empty()
            self.__render_graph_element(graph_placeholder, None)

        try:
            for chunk in graph.stream(
                input=graph_input,
                context=graph_context,
                stream_mode="updates",
                config={"recursion_limit": 100},
            ):
                st.write(chunk)
                st.write(self.__stream_generator)

        except Exception as e:
            st.session_state["error_toast"] = True
            st.error(f"Graph execution failed: {e}")

    def __render_graph_element(self, graph_placeholder: DeltaGenerator, node_state: dict[str, Any] | None) -> None:
        """
        Renders the graph element in the user interface.
        """
        graph_placeholder.image(
            image=f"{images_source_path}/{node_state['next_node']}.png"
            if node_state
            else f"{images_source_path}/intent_comprehension.png",
            width="stretch",
        )

    def __stream_generator(self) -> Generator[str, None, None]:
        """
        Generator to stream the thinking or chat output word by word.
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

    def __show_toast_message(self) -> None:
        """
        Shows toast messages based on the session state.
        """
        if st.session_state["success_toast"]:
            st.session_state["success_toast"] = False

            st.toast(
                body="###### **Your request is completed.**",
                duration="long",
            )

        if st.session_state["punt_toast"]:
            self.__render_chat_turn_block(chat_turn=st.session_state["punt_response"])
            st.session_state["punt_toast"] = False
            st.session_state["punt_response"] = []

            st.toast(
                body="###### **Your request is out of business analytics domain. This chat turn will not be persisted.**",
                duration="long",
            )

        if st.session_state["error_toast"]:
            st.session_state["error_toast"] = False

            st.toast(
                body="###### **System fails to process your request. Please try again.**",
                duration="long",
            )
