# standard
from pathlib import Path

dataset_file_path: Path = Path(__file__).resolve().parent / "dataset.csv"


def unlink_dataset_file():
    """
    Unlink the dataset file if it exists.
    """
    if dataset_file_path.exists():
        dataset_file_path.unlink()


__all__ = [
    "dataset_file_path",
    "unlink_dataset_file",
]
