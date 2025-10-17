from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import csv
import os
import json
from utils.logging_utils import setup_logging
from configs.constants import Config


def load_data():
    logger = setup_logging(log_dir=Config.LOGGER_INGESTION_DIR, log_file_prefix="data_pipeline")

    logger.info("Starting data loading process")
    
    try:
        reviews_data = []
        returns_data = []
        sales_data = []

        logger.info("Loading reviews data")
        with open(os.path.join(Config.REVIEW_DATA_DIR, "sde2_reviews.csv"), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                reviews_data.append(row)
        logger.info("Loaded {} review records".format(len(reviews_data)))

        logger.info("Loading returns data")
        with open(os.path.join(Config.RETURN_DATA_DIR, "sde2_returns.csv"), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                returns_data.append(row)
        logger.info("Loaded {} return records".format(len(returns_data)))

        logger.info("Loading sales data")
        with open(os.path.join(Config.SALES_DATA_DIR, "sde2_sales.csv"), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sales_data.append(row)
        logger.info("Loaded {} sales records".format(len(sales_data)))

        logger.info("Processing returns aggregation")
        returns_agg = {}
        for row in returns_data:
            asin = row["asin"].strip()
            reason = row["return_reason"].strip()
            count = int(row["count"])

            if asin not in returns_agg:
                returns_agg[asin] = {}

            if reason not in returns_agg[asin]:
                returns_agg[asin][reason] = 0

            returns_agg[asin][reason] += count

        logger.info("Processing reviews grouping")
        reviews_grouped = {}
        for row in reviews_data:
            asin = row["asin"].strip()
            review_text = row["review_text"].strip()
            rating_value = row["rating"].strip()

            try:
                rating = float(rating_value)
            except ValueError:
                rating = rating_value

            if asin not in reviews_grouped:
                reviews_grouped[asin] = []

            reviews_grouped[asin].append({"review_text": review_text, "rating": rating})

        logger.info("Processing sales grouping")
        sales_grouped = {}
        for row in sales_data:
            asin = row["asin"].strip()

            if asin not in sales_grouped:
                sales_grouped[asin] = []

            sales_grouped[asin].append(
                {
                    "week": int(row["week"]),
                    "units_sold": int(row["units_sold"]),
                    "gmv": int(row["gmv"]),
                    "refunds": int(row["refunds"]),
                }
            )

        logger.info("Merging all data")
        all_asins = set(
            list(returns_agg.keys())
            + list(reviews_grouped.keys())
            + list(sales_grouped.keys())
        )
        merged_data = {}

        for asin in sorted(all_asins):
            asin_returns = []
            if asin in returns_agg:
                for reason, count in returns_agg[asin].items():
                    asin_returns.append({"reason": reason, "count": count})

            asin_reviews = reviews_grouped.get(asin, [])
            asin_sales = sales_grouped.get(asin, [])

            merged_data[asin] = {
                "returns": asin_returns,
                "reviews": asin_reviews,
                "weekly_sales": asin_sales,
            }

        logger.info("Merged data for {} ASINs".format(len(merged_data)))

        os.makedirs(Config.OUTPUT_INGESTION_DIR, exist_ok=True)
        output_path = os.path.join(Config.OUTPUT_INGESTION_DIR, "merged_data.json")

        logger.info("Saving merged data to {}".format(output_path))
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)

        logger.info("Data loading process completed successfully")
        return merged_data

    except Exception as e:
        logger.error("Error in data loading process: {}".format(str(e)))
        raise

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 15),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'data_pipeline',
    default_args=default_args,
    description='Data ingestion pipeline for merging reviews, returns, and sales data',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['ingestion', 'data-pipeline']
)

load_data_task = PythonOperator(
    task_id='load_and_merge_data',
    python_callable=load_data,
    dag=dag,
)