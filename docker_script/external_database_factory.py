# pyright: reportUnknownMemberType=false

# standard
import os
import re
import time
from pathlib import Path
from typing import Any

# third-party
import pandas as pd
from pandas import DataFrame
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Engine,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    create_engine,
    insert,
    text,
)

# internal
from context.database import external_db_url

_CHUNK_SIZE: int = 5_000
_LEGACY_TABLES: tuple[str, ...] = ("sale_transactions",)
_DATE_LIKE_COLUMN: re.Pattern[str] = re.compile(
    r"(?:^|_)(?:date|timestamp)(?:$|_)|^saledate$|^order_date$|^created_at$|^updated_at$",
    re.IGNORECASE,
)
_DATASETS_DIR: Path = Path(__file__).resolve().parent / "datasets"
_DATASETS_DOC: Path = _DATASETS_DIR / "DATASETS.md"


def _parse_dataset_id(raw: str) -> int:
    """
    Parse EXTERNAL_DATASET values such as ``1`` or ``dataset_1``.
    """
    value: str = raw.strip()
    match: re.Match[str] | None = re.fullmatch(r"dataset_(\d+)", value, re.IGNORECASE)

    if match:
        dataset_id: int = int(match.group(1))
    else:
        dataset_id = int(value)

    if dataset_id not in (1, 2, 3, 4):
        raise ValueError(f"EXTERNAL_DATASET must be 1-4 or dataset_1 ... dataset_4, got {raw!r}")

    return dataset_id


def _resolve_csv_path(dataset_id: int) -> Path:
    """
    Resolve the local CSV path for a dataset id.
    """
    csv_path: Path = _DATASETS_DIR / f"dataset_{dataset_id}.csv"

    if not csv_path.is_file():
        raise FileNotFoundError(
            f"Dataset file not found: {csv_path}. "
            f"Download CSVs listed in {_DATASETS_DOC} into {_DATASETS_DIR}/."
        )

    return csv_path


def _to_snake_case(name: str) -> str:
    """
    Normalize a CSV header into a PostgreSQL-friendly snake_case identifier.
    """
    normalized: str = name.strip()
    normalized = re.sub(r"[^\w\s]", "", normalized)
    normalized = re.sub(r"\s+", "_", normalized)
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized)
    normalized = normalized.lower().strip("_")

    if not normalized:
        raise ValueError(f"Could not normalize column name {name!r}")

    return normalized


def _normalize_columns(df: DataFrame) -> DataFrame:
    """
    Rename DataFrame columns to unique snake_case identifiers.
    """
    seen: dict[str, int] = {}
    rename_map: dict[str, str] = {}

    for column in df.columns:
        base_name: str = _to_snake_case(str(column))
        count: int = seen.get(base_name, 0)
        seen[base_name] = count + 1
        rename_map[column] = base_name if count == 0 else f"{base_name}_{count + 1}"

    return df.rename(columns=rename_map)


def _coerce_booleans(df: DataFrame) -> DataFrame:
    """
    Convert object columns that only contain true/false literals into booleans.
    """
    out: DataFrame = df.copy()

    for column in out.columns:
        if out[column].dtype != object:
            continue

        non_null = out[column].dropna()
        if non_null.empty:
            continue

        lowered: pd.Series[Any] = non_null.astype(str).str.lower()
        if lowered.isin({"true", "false"}).all():
            out[column] = out[column].map(
                lambda value: str(value).lower() == "true" if pd.notnull(value) else None
            )

    return out


def _parse_datetimes(df: DataFrame) -> DataFrame:
    """
    Parse likely datetime columns based on name heuristics and pandas inference.
    """
    out: DataFrame = df.copy()

    for column in out.columns:
        if not _DATE_LIKE_COLUMN.search(str(column)):
            continue

        parsed: pd.Series[Any] = pd.to_datetime(out[column], errors="coerce", utc=False)
        if parsed.notna().any():
            out[column] = parsed

    return out


def _sqlalchemy_column(name: str, dtype: Any) -> Column[Any]:
    """
    Map a pandas dtype to a SQLAlchemy column definition.
    """
    if pd.api.types.is_bool_dtype(dtype):
        return Column(name, Boolean, nullable=True)

    if pd.api.types.is_integer_dtype(dtype):
        return Column(name, Integer, nullable=True)

    if pd.api.types.is_float_dtype(dtype):
        return Column(name, Numeric(18, 4), nullable=True)

    if pd.api.types.is_datetime64_any_dtype(dtype):
        return Column(name, DateTime, nullable=True)

    return Column(name, String, nullable=True)


def _build_table(metadata: MetaData, table_name: str, df: DataFrame) -> Table:
    """
    Build a SQLAlchemy table from inferred DataFrame dtypes.
    """
    columns: list[Column[Any]] = [_sqlalchemy_column(str(name), dtype) for name, dtype in df.dtypes.items()]
    return Table(table_name, metadata, *columns)


def _records_from_df(df: DataFrame) -> list[dict[str, Any]]:
    """
    Convert a DataFrame into insert-ready records with NULLs instead of NaN.
    """
    return [
        {str(key): (None if pd.isna(value) else value) for key, value in row.items()}
        for row in df.to_dict(orient="records")
    ]


def _drop_tables(engine: Engine, table_names: tuple[str, ...]) -> None:
    """
    Drop seeded tables if they already exist from a previous run.
    """
    with engine.begin() as connection:
        for table_name in table_names:
            connection.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))


def _seed_table(engine: Engine, table: Table, df: DataFrame) -> None:
    """
    Recreate and populate the target table using chunked inserts.
    """
    metadata: MetaData = table.metadata
    metadata.create_all(bind=engine, checkfirst=True)

    records: list[dict[str, Any]] = _records_from_df(df)

    with engine.begin() as connection:
        for start in range(0, len(records), _CHUNK_SIZE):
            chunk: list[dict[str, Any]] = records[start : start + _CHUNK_SIZE]
            connection.execute(insert(table), chunk)


def _load_dataset_frame(csv_path: Path) -> DataFrame:
    """
    Load and normalize a dataset CSV for seeding.
    """
    df: DataFrame = pd.read_csv(csv_path)
    df = _normalize_columns(df)
    df = _coerce_booleans(df)
    df = _parse_datetimes(df)
    return df


def main() -> None:
    """
    Populate the external database with a selected local business dataset CSV.
    """
    if os.getenv("ENABLE_EXTERNAL_DB_SEEDING", "true").lower() != "true":
        return

    dataset_id: int = _parse_dataset_id(os.getenv("EXTERNAL_DATASET", "1"))
    table_name: str = os.getenv("EXTERNAL_DB_TABLE_NAME", "business_data").strip()

    if not table_name:
        raise ValueError("EXTERNAL_DB_TABLE_NAME must not be empty")

    csv_path: Path = _resolve_csv_path(dataset_id)
    engine: Engine = create_engine(external_db_url)

    started_at: float = time.perf_counter()
    df: DataFrame = _load_dataset_frame(csv_path)

    tables_to_drop: tuple[str, ...] = tuple(dict.fromkeys((table_name, *_LEGACY_TABLES)))
    _drop_tables(engine, tables_to_drop)

    metadata: MetaData = MetaData()
    table: Table = _build_table(metadata, table_name, df)
    _seed_table(engine, table, df)

    elapsed_s: float = time.perf_counter() - started_at
    print(
        f"Seeded external database table '{table_name}' "
        f"from {csv_path.name} ({len(df)} rows, {len(df.columns)} columns) "
        f"in {elapsed_s:.1f}s"
    )


if __name__ == "__main__":
    main()
