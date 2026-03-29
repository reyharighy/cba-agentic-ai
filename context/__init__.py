# internal
from typing import Literal
from .manager import ContextManager


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


__all__ = [
    "ContextManager",
    "load_analytical_sandbox_bootstrap",
    "load_infographic_sandbox_bootstrap",
]
