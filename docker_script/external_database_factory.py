# standard
import os
from typing import (
    Any,
    Dict,
    List,
)

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
)
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

# internal
from context.database.config import external_db_url

def main() -> None:
    if os.getenv("ENABLE_EXTERNAL_DB_SEEDING", "true").lower() != "true":
        print("External database seeding is disabled.")
        return

    engine: Engine = create_engine(external_db_url)
    metadata: MetaData = MetaData()
    table: Table = Table(
        "sale_transactions",
        metadata,
        Column("id", UUID(as_uuid=True), nullable=False, primary_key=True, unique=True, default=uuid4),
        Column("hour_of_day", Integer, nullable=False),
        Column("payment_type", String, nullable=False),
        Column("net_price", Numeric(10, 2), nullable=False),
        Column("coffee_name", String, nullable=False),
        Column("time_of_day", String, nullable=False),
        Column("day_name", String, nullable=False),
        Column("is_weekend", Boolean, nullable= False),
        Column("month_name", String, nullable=False),
        Column("day_sort", Integer, nullable=False),
        Column("month_sort", Integer, nullable=False),
        Column("created_at", DateTime, nullable=False)
    )

    metadata.create_all(engine)

    df: DataFrame = pd.read_csv("./docker_script/synthetic_data.csv")
    df["created_at"] = pd.to_datetime(df["created_at"])

    records: List[Dict[str, Any]] = [
        {str(k): v for k, v in row.items()}
        for row in df.to_dict(orient="records")
    ]

    for r in records:
        r["id"] = uuid4()

    with engine.begin() as connection:
        connection.execute(insert(table), records)

    print("External database is successfully populated with synthetic data.")

if __name__ == "__main__":
    main()
