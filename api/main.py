# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false

# standard
import uuid
from collections.abc import Iterator
from contextlib import asynccontextmanager

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

    def event_generator() -> Iterator[str]:
        try:
            for event in graph.stream(
                input=graph_input,
                context=graph_context,  # type: ignore[arg-type]
                stream_mode="updates",
                config=config,
            ):
                payload: str = json.dumps(jsonable_encoder({
                    "type": "update",
                    "data": event,
                }))

                yield f"data: {payload}\n\n"

            graph_state: StateSnapshot = graph.get_state(config)

            if graph_state.next:
                for task in graph_state.tasks:
                    for interrupt in task.interrupts:
                        payload = json.dumps({
                            "type": "interrupt",
                            "thread_id": thread_id,
                            "data": interrupt.value,
                        })

                        yield f"data: {payload}\n\n"
            else:
                app.state.thread_contexts.pop(thread_id, None)
                yield "data: {\"type\": \"complete\"}\n\n"

        except Exception as e:
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

@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
