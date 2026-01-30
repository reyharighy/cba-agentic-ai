# pyright: reportMissingTypeStubs=false

# standard
from importlib.abc import Loader
from importlib.util import (
    module_from_spec,
    spec_from_file_location,
)
from pathlib import Path
from types import ModuleType
from typing import Literal

# third-party
from langchain_core.language_models import BaseChatModel
from langgraph.graph.state import CompiledStateGraph

# internal
from agent import (
    Graph,
    Context,
    State,
)
from context.database import (
    ContextManager,
    external_db_url,
)
from context.system_prompts import prompt_dict
from language_model.provider import groq_gpt_120b_high
from memory.database import (
    MemoryManager,
    internal_db_url,
)
from util import st_cache


@st_cache("Setting up application data and resources", "data")
def cold_start() -> None:
    """
    Cold start function to initialize application data and resources.
    """
    load_memory_manager()
    load_context_manager()
    load_language_model()
    load_graph()
    load_prompts_set()
    load_analytical_sandbox_bootstrap()
    load_infographic_sandbox_bootstrap()


@st_cache("Loading database manager", "resource")
def load_memory_manager() -> MemoryManager:
    """
    Loads the MemoryManager instance.
    """
    return MemoryManager(internal_db_url)


@st_cache("Loading context manager", "resource")
def load_context_manager() -> ContextManager:
    """
    Loads the ContextManager instance.
    """
    return ContextManager(external_db_url)


@st_cache("Loading language models", "resource")
def load_language_model() -> BaseChatModel:
    """
    Loads the language model instance.
    """
    return groq_gpt_120b_high


@st_cache("Loading graph", "resource")
def load_graph() -> CompiledStateGraph[State, Context]:
    """
    Loads and builds the state graph.
    """
    context_manager: ContextManager = load_context_manager()
    memory_manager: MemoryManager = load_memory_manager()
    language_model: BaseChatModel = load_language_model()

    graph = Graph(
        context_manager=context_manager,
        memory_manager=memory_manager,
        language_model=language_model,
    )

    return graph.build_graph()


@st_cache("Loading prompts set", "data")
def load_prompts_set() -> dict[str, str]:
    """
    Loads the set of system prompts.
    """
    return prompt_dict


@st_cache("Loading analytical sandbox bootstrap", "data")
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


@st_cache("Loading infographic sandbox bootstrap", "data")
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


@st_cache("Loading infographic object", "resource")
def load_infographic(infographic_object_file_path: Path) -> tuple[Loader | None, ModuleType | None]:
    """
    Loads an infographic object from the specified file path.
    """
    spec = spec_from_file_location(
        name=infographic_object_file_path.stem,
        location=infographic_object_file_path,
    )

    return (spec.loader, module_from_spec(spec)) if spec else (None, None)
