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
        Column(
            "id", UUID(as_uuid=True), nullable=False, primary_key=True, unique=True, default=uuid4,
            comment="Unique identifier for each sale transaction record."
        ),
        Column(
            "hour_of_day", Integer, nullable=False,
            comment="Hour of the day when the transaction occurred, represented as an integer from 0 to 23."
        ),
        Column(
            "payment_type", String, nullable=False,
            comment="Method of payment used for the transaction."
        ),
        Column(
            "net_price", Numeric(10, 2), nullable=False,
            comment="Final transaction amount after deductions, stored in USD currency units."
        ),
        Column(
            "coffee_name", String, nullable=False,
            comment="Name or variant of the coffee product sold in the transaction."
        ),
        Column(
            "time_of_day", String, nullable=False,
            comment="Categorical label representing the time segment of the day."
        ),
        Column(
            "day_name", String, nullable=False,
            comment="Name of the weekday on which the transaction occurred."
        ),
        Column(
            "is_weekend", Boolean, nullable= False,
            comment="Boolean flag indicating whether the transaction occurred on a weekend."
        ),
        Column(
            "month_name", String, nullable=False,
            comment="Name of the month in which the transaction occurred."
        ),
        Column(
            "day_sort", Integer, nullable=False,
            comment="Numeric day-of-week value used for chronological sorting within a week."
        ),
        Column(
            "month_sort", Integer, nullable=False,
            comment="Numeric month value used for chronological sorting within a year."
        ),
        Column(
            "created_at", DateTime, nullable=False,
            comment="Exact timestamp when the transaction was recorded."
        )
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
