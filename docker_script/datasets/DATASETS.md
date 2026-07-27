# Local Seed Datasets

CSV files in this directory are used to populate the external PostgreSQL database on container startup. Files are **not committed** to Git (see `.gitignore`). Download datasets locally from the sources below.

| ID | Local file | Domain | Source |
| -- | ---------- | ------ | ------ |
| 1 | `dataset_1.csv` | Coffee retail sales | [Coffee Sales Dataset (Kaggle)](https://www.kaggle.com/datasets/navjotkaushal/coffee-sales-dataset) |
| 2 | `dataset_2.csv` | Vehicle sales | [Vehicle Sales Data (Kaggle)](https://www.kaggle.com/datasets/syedanwarafridi/vehicle-sales-data) |
| 3 | `dataset_3.csv` | E-commerce sales | [Ecommerce Sales Data (Kaggle)](https://www.kaggle.com/datasets/uzmaakhtar/ecommerce-sales-data) |
| 4 | `dataset_4.csv` | Customer churn / CRM | [Customer Churn Prediction Business Dataset (Kaggle)](https://www.kaggle.com/datasets/miadul/customer-churn-prediction-business-dataset) |
| 5 | `dataset_5.csv` | Chocolate sales | [Chocolate Sales (Kaggle)](https://www.kaggle.com/datasets/atharvasoundankar/chocolate-sales) |

## Seeding the external database

On container startup, [`external_database_factory.py`](../external_database_factory.py) loads one CSV into PostgreSQL when `ENABLE_EXTERNAL_DB_SEEDING=true`:

| `EXTERNAL_DATASET` | File loaded |
| ------------------ | ----------- |
| `1` or `dataset_1` | `dataset_1.csv` (default) |
| `2` or `dataset_2` | `dataset_2.csv` |
| `3` or `dataset_3` | `dataset_3.csv` |
| `4` or `dataset_4` | `dataset_4.csv` |
| `5` or `dataset_5` | `dataset_5.csv` |

Rows are stored in table `business_data` by default (`EXTERNAL_DB_TABLE_NAME`). Restart the container after changing `EXTERNAL_DATASET` in `.env`.

## Attribution

When reusing these datasets, cite the respective Kaggle dataset pages and follow each dataset's license terms on Kaggle.
