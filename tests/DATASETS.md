# Local Seed Datasets

CSV files in `docker_script/datasets/` are used for multi-domain testing and are **not committed** to Git (see `.gitignore`). Download the files locally from the sources below.

Each profile **P1–P5** maps to `dataset_N.csv` (for example, P1 → `dataset_1.csv`). Test reports for each profile live under [`tests/`](.).

| Profile | Local file | Domain | Source |
| ------- | ---------- | ------ | ------ |
| **P1** | `dataset_1.csv` | Coffee retail sales (reference profile) | [Coffee Sales Dataset (Kaggle)](https://www.kaggle.com/datasets/navjotkaushal/coffee-sales-dataset) |
| **P2** | `dataset_2.csv` | Vehicle sales | [Vehicle Sales Data (Kaggle)](https://www.kaggle.com/datasets/syedanwarafridi/vehicle-sales-data) |
| **P3** | `dataset_3.csv` | E-commerce sales | [Ecommerce Sales Data (Kaggle)](https://www.kaggle.com/datasets/uzmaakhtar/ecommerce-sales-data) |
| **P4** | `dataset_4.csv` | Customer churn / CRM | [Customer Churn Prediction Business Dataset (Kaggle)](https://www.kaggle.com/datasets/miadul/customer-churn-prediction-business-dataset) |
| **P5** | `dataset_5.csv` | Chocolate sales | [Chocolate Sales (Kaggle)](https://www.kaggle.com/datasets/atharvasoundankar/chocolate-sales) |

**P1** is the reference profile with the most detailed scenario documentation. **P2–P5** run the same S1–S8 orchestration scenarios on different business schemas to verify cross-domain behavior.

## Seeding the external database

On container startup, [`external_database_factory.py`](../docker_script/external_database_factory.py) loads one CSV into PostgreSQL:

| `EXTERNAL_DATASET` | Profile | File loaded |
| ------------------ | ------- | ----------- |
| `1` or `dataset_1` | P1 | `dataset_1.csv` (default) |
| `2` or `dataset_2` | P2 | `dataset_2.csv` |
| `3` or `dataset_3` | P3 | `dataset_3.csv` |
| `4` or `dataset_4` | P4 | `dataset_4.csv` |
| `5` or `dataset_5` | P5 | `dataset_5.csv` |

Rows are stored in table `business_data` by default (`EXTERNAL_DB_TABLE_NAME`). Restart the container after changing `EXTERNAL_DATASET` in `.env`.

## Attribution

When reusing these datasets, cite the respective Kaggle dataset pages and follow each dataset’s license terms on Kaggle.
