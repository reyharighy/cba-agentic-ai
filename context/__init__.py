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
    inferential: str = ignore_warnings + pandas + numpy + scipy + df_load
    predictive: str = ignore_warnings + pandas + numpy + sklearn + df_load

    return {
        "descriptive": descriptive,
        "diagnostic": diagnostic,
        "inferential": inferential,
        "predictive": predictive,
    }


__all__ = [
    "ContextManager",
    "load_analytical_sandbox_bootstrap",
]
