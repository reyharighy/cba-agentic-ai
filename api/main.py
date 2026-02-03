# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false

# standard
from collections.abc import Iterator
from typing_extensions import Literal

# third
import json
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

# internal
from agent.graph import Graph
from agent.runtime import Context
from agent.state import State
from api.schemas import AgentRequest
from context.system_prompts import prompt_dict


app = FastAPI(
    title="Conversational Business Analytics - Agentic AI API",
    version="0.1.0",
)


def load_analytical_sandbox_bootstrap() -> dict[Literal["descriptive", "diagnostic", "predictive", "inferential"], str]:
    """
    Loads the analytical sandbox bootstrap code snippets.
    """
    ignore_warnings: str = "import warnings\n"
    ignore_warnings += "warnings.filterwarnings('ignore')\n"
    pandas: str = "import pandas as pd\n"
    numpy: str = "import numpy as np\n"
    scipy: str = "import scipy\n"
    sklearn: str = "import sklearn\n"
    df_load: str = "df = pd.read_csv('dataset.csv')\n"
    df_load += "\n" + "for column in df.columns:"
    df_load += "\n\t" + "if pd.api.types.is_object_dtype(df[column]):"
    df_load += "\n\t\t" + "try:"
    df_load += "\n\t\t\t" + "df[column] = pd.to_datetime(df[column])"
    df_load += "\n\t\t" + "except Exception as _:"
    df_load += "\n\t\t\t" + "pass\n"

    descriptive: str = ignore_warnings + pandas + numpy + df_load
    diagnostic: str = ignore_warnings + pandas + numpy + scipy + df_load
    predictive: str = ignore_warnings + pandas + numpy + scipy + df_load
    inferential: str = ignore_warnings + pandas + numpy + sklearn + df_load

    return {
        "descriptive": descriptive,
        "diagnostic": diagnostic,
        "predictive": predictive,
        "inferential": inferential,
    }


def load_infographic_sandbox_bootstrap() -> str:
    """
    Loads the infographic sandbox bootstrap code snippet.
    """
    warnings: str = "import warnings\n"
    pandas: str = "import pandas as pd\n"
    numpy: str = "import numpy as np\n"
    graph_objects: str = "import plotly.graph_objects as go\n"
    express: str = "import plotly.express as px\n\n"
    ignore_warnings: str = "warnings.filterwarnings('ignore')\n"
    df_load: str = "df = pd.read_csv('dataset.csv')\n"
    df_transform: str = "\n" + "for column in df.columns:"
    df_transform += "\n\t" + "if pd.api.types.is_object_dtype(df[column]):"
    df_transform += "\n\t\t" + "try:"
    df_transform += "\n\t\t\t" + "df[column] = pd.to_datetime(df[column])"
    df_transform += "\n\t\t" + "except Exception as _:"
    df_transform += "\n\t\t\t" + "pass\n\n"

    return warnings + pandas + numpy + graph_objects + express + ignore_warnings + df_load + df_transform


@app.post("/agent/stream")
def run_agent(request: AgentRequest):
    """
    Endpoint to run the agent and stream responses.
    """
    graph = Graph().build_graph()

    graph_input: State = State(
        messages=[HumanMessage(content=request.input)],
        ui_payload=None,
        current_node=None,
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
        turn_num=request.turn_num,
        prompts_set=prompt_dict,
        analytical_sandbox_bootstrap=load_analytical_sandbox_bootstrap(),
        infographic_sandbox_bootstrap=load_infographic_sandbox_bootstrap(),
    )

    def event_generator() -> Iterator[str]:
        try:
            for event in graph.stream(
                input=graph_input,
                context=graph_context,
                stream_mode="updates",
                config={"recursion_limit": 100},
            ):
                safe_event = jsonable_encoder(event)
                yield json.dumps(safe_event) + "\n\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
