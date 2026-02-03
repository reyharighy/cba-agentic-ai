# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false

# standard
from collections.abc import Iterator
from contextlib import asynccontextmanager

# third
import json
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse

# internal
from agent.graph import Graph
from agent.runtime import Context
from agent.state import State, make_initial_state
from api.schemas import AgentRequest
from context import load_analytical_sandbox_bootstrap, load_infographic_sandbox_bootstrap
from context.system_prompts import prompt_dict
from memory import MemoryManager
from memory.database import internal_db_url
from memory.models.chat_history import ChatHistory


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.graph = Graph().build_graph()
    app.state.prompts_set = prompt_dict
    app.state.analytical_sandbox_bootstrap = load_analytical_sandbox_bootstrap()
    app.state.infographic_sandbox_bootstrap = load_infographic_sandbox_bootstrap()
    app.state.memory_manager = MemoryManager(internal_db_url)

    yield


app = FastAPI(
    title="Conversational Business Analytics - Agentic AI API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.post("/agent/stream")
def run_agent(request: AgentRequest):
    """
    Endpoint to run the agent and stream responses.
    """
    graph = app.state.graph
    graph_input: State = make_initial_state(user_input=request.input)
    chat_history: list[ChatHistory] = app.state.memory_manager.index_chat_history()
    turn_num: int = max(chat.turn_num for chat in chat_history) if chat_history else 0

    graph_context: Context = Context(
        turn_num=turn_num + 1,
        prompts_set=app.state.prompts_set,
        analytical_sandbox_bootstrap=app.state.analytical_sandbox_bootstrap,
        infographic_sandbox_bootstrap=app.state.infographic_sandbox_bootstrap,
    )

    def event_generator() -> Iterator[str]:
        try:
            for event in graph.stream(
                input=graph_input,
                context=graph_context,
                stream_mode="updates",
                config={"recursion_limit": 100},
            ):
                yield "\n" + json.dumps(jsonable_encoder(event)) + "\n"

        except Exception as e:
            yield "\n" + json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
