# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false

# standard
import uuid
from collections.abc import Iterator
from contextlib import asynccontextmanager
from typing import (
    Any,
    Literal
)

# third
import json
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.pregel.types import StateSnapshot
from langgraph.types import Command

# internal
from agent.graph import Graph
from agent.runtime import Context, read_enable_infographic_from_env
from agent.state import State, make_initial_state
from api.schemas import AgentRequest, ResumeRequest
from context import load_analytical_sandbox_bootstrap, load_infographic_sandbox_bootstrap
from context.system_prompts import prompt_dict
from memory import MemoryManager
from memory.database import internal_db_url
from memory.models import (
    StateTransition,
    StateTransitionCreate,
    StateTransitionShow,
)
from memory.models.chat_history import ChatHistory


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.enable_infographic = read_enable_infographic_from_env()
    app.state.graph = Graph().build_graph()
    app.state.prompts_set = prompt_dict
    app.state.analytical_sandbox_bootstrap = load_analytical_sandbox_bootstrap()
    app.state.infographic_sandbox_bootstrap = load_infographic_sandbox_bootstrap()
    app.state.memory_manager = MemoryManager(internal_db_url)
    app.state.thread_contexts = {}  # dict[str, Context]

    yield


app = FastAPI(
    title="Conversational Business Analytics - Agentic AI API",
    version="0.1.0",
    lifespan=lifespan,
)


def _stream_graph(
    graph_input: State | Command[str],
    graph_context: Context,
    thread_id: str,
) -> StreamingResponse:
    """
    Shared streaming logic for both initial runs and resumed runs.
    """
    graph: CompiledStateGraph[State] = app.state.graph

    config: RunnableConfig = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 100,
    }

    def _persist_transition(
        sequence_num: int,
        node_name: str,
        event_type: Literal['update', 'interrupt', 'complete', 'error'],
        payload: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> None:
        """
        Persist a redacted transition row into the agent DB audit log.

        Verbatim payloads are intentionally not stored; only a sha256 digest,
        byte size, and short preview are kept (see memory.models.state_transition).
        """
        create_state_transition_params: StateTransitionCreate = StateTransitionCreate(
            thread_id=thread_id,
            turn_num=graph_context.turn_num,
            sequence_num=sequence_num,
            node_name=node_name,
            event_type=event_type,
            payload=payload,
            error_message=error_message,
        )

        app.state.memory_manager.store_state_transition(create_state_transition_params())

    def event_generator() -> Iterator[str]:
        sequence_num: int = 0

        try:
            for event in graph.stream(
                input=graph_input,
                context=graph_context,  # type: ignore[arg-type]
                stream_mode="updates",
                config=config,
            ):
                sequence_num += 1
                encoded_event: dict[str, Any] = jsonable_encoder(event)

                node_name: str = next(iter(encoded_event.keys()))

                _persist_transition(
                    sequence_num=sequence_num,
                    node_name=node_name,
                    event_type="update",
                    payload=encoded_event,
                )

                payload: str = json.dumps({
                    "type": "update",
                    "data": encoded_event,
                })

                yield f"data: {payload}\n\n"

            graph_state: StateSnapshot = graph.get_state(config)

            if graph_state.next:
                for task in graph_state.tasks:
                    for interrupt in task.interrupts:
                        sequence_num += 1
                        encoded_interrupt: Any = jsonable_encoder(interrupt.value)

                        _persist_transition(
                            sequence_num=sequence_num,
                            node_name=task.name or "<interrupt>",
                            event_type="interrupt",
                            payload=encoded_interrupt,
                        )

                        payload = json.dumps({
                            "type": "interrupt",
                            "thread_id": thread_id,
                            "data": encoded_interrupt,
                        })

                        yield f"data: {payload}\n\n"
            else:
                sequence_num += 1

                _persist_transition(
                    sequence_num=sequence_num,
                    node_name="<complete>",
                    event_type="complete",
                )

                app.state.thread_contexts.pop(thread_id, None)
                yield "data: {\"type\": \"complete\"}\n\n"

        except Exception as e:
            sequence_num += 1

            _persist_transition(
                sequence_num=sequence_num,
                node_name="<error>",
                event_type="error",
                error_message=str(e),
            )

            app.state.thread_contexts.pop(thread_id, None)

            payload = json.dumps({
                "type": "error",
                "message": str(e),
            })

            yield f"data: {payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/agent/stream")
def run_agent(request: AgentRequest) -> StreamingResponse:
    """
    Endpoint to run the agent and stream responses.
    """
    graph_input: State = make_initial_state(user_input=request.input)
    chat_history: list[ChatHistory] = app.state.memory_manager.index_chat_history()
    turn_num: int = max(chat.turn_num for chat in chat_history) if chat_history else 0

    graph_context: Context = Context(
        turn_num=turn_num + 1,
        prompts_set=app.state.prompts_set,
        analytical_sandbox_bootstrap=app.state.analytical_sandbox_bootstrap,
        infographic_sandbox_bootstrap=app.state.infographic_sandbox_bootstrap,
        enable_infographic=app.state.enable_infographic,
    )

    thread_id: str = str(uuid.uuid4())
    app.state.thread_contexts[thread_id] = graph_context

    return _stream_graph(graph_input, graph_context, thread_id)


@app.post("/agent/resume")
def resume_agent(request: ResumeRequest) -> StreamingResponse:
    """
    Endpoint to resume an interrupted agent run with additional user context.
    """
    graph_context: Context | None = app.state.thread_contexts.get(request.thread_id)

    if not graph_context:
        raise HTTPException(
            status_code=404,
            detail=f"Thread '{request.thread_id}' not found or already completed.",
        )

    return _stream_graph(Command(resume=request.input), graph_context, request.thread_id)

@app.get("/chat/history")
async def get_chat_history() -> list[ChatHistory]:
    """
    Endpoint to retrieve chat history.
    """
    return app.state.memory_manager.index_chat_history()

@app.get("/agent/audit/{thread_id}")
def get_state_transitions(thread_id: str) -> list[StateTransition]:
    """
    Endpoint to retrieve the persisted, redacted state-transition audit log for a given thread.
    """
    show_params: StateTransitionShow = StateTransitionShow(thread_id=thread_id)

    return app.state.memory_manager.index_state_transitions_by_thread(show_params)

@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
