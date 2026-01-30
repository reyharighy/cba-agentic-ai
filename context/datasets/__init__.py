# standard
from pathlib import Path

dataset_file_path: Path = Path(__file__).resolve().parent / "dataset.csv"

__all__ = ["dataset_file_path"]
