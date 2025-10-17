from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os
import json
from datetime import datetime
from utils.logging_utils import setup_logging
from configs.constants import Config


def top_issues_based_on_returns():
    logger = setup_logging(log_dir=Config.LOGGER_INSIGHTS_DIR, log_file_prefix="top_issues_based_on_returns")
    logger.info("Starting top issues analysis based on returns")
    
    try:
        logger.info("Loading merged data")
        with open(os.path.join(Config.OUTPUT_INGESTION_DIR, "merged_data.json"), "r") as file:
            data = json.load(file)
        logger.info("Loaded data for {} ASINs".format(len(data)))

        logger.info("Loading return suggestions")
        with open(os.path.join(Config.SUGGESTION_DIR, "returns.json"), "r") as suggestion_file:
            suggestions = json.load(suggestion_file)
        logger.info("Loaded {} return suggestions".format(len(suggestions)))

        result = {}
        processed_count = 0

        for asin, asin_data in data.items():
            returns = asin_data.get("returns", [])
            if not returns:
                result[asin] = {
                    "top_reason": None,
                    "suggestion": "No return data available",
                }
                logger.debug("ASIN {}: No return data available".format(asin))
                continue

            top_reason_entry = max(returns, key=lambda r: r.get("count", 0))
            top_reason = top_reason_entry.get("reason")
            suggestion = suggestions.get(
                top_reason, "No suggestion available for this reason"
            )

            result[asin] = {"top_reason": top_reason, "suggestion": suggestion}
            processed_count += 1
            logger.debug("ASIN {}: Top reason = {}".format(asin, top_reason))

        logger.info("Processed {} ASINs with return data".format(processed_count))

        
        os.makedirs(Config.OUTPUT_INSIGHTS_DIR, exist_ok=True)
        logger.info("Created/verified directory: {}".format(Config.OUTPUT_INSIGHTS_DIR))
        logger.info("Directory exists: {}".format(os.path.exists(Config.OUTPUT_INSIGHTS_DIR)))
        
        output_path = os.path.join(
            Config.OUTPUT_INSIGHTS_DIR, "top_issues_based_on_returns.json"
        )
        logger.info("Saving results to {}".format(output_path))
        
        parent_dir = os.path.dirname(output_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
            logger.info("Created parent directory: {}".format(parent_dir))
        
        with open(output_path, "w") as outfile:
            json.dump(result, outfile, indent=4)
        
        logger.info("Output written to {}".format(output_path))
        logger.info("Top issues analysis based on returns completed successfully")
        return result

    except FileNotFoundError as e:
        logger.error("File not found: {}".format(e.filename))
        raise
    except json.JSONDecodeError as e:
        logger.error("JSON decode error: {}".format(str(e)))
        raise
    except Exception as e:
        logger.error("Error in top issues analysis: {}".format(str(e)))
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
    'top_issues_based_on_returns',
    default_args=default_args,
    description='Analyze top return issues and provide suggestions',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['insights', 'returns-analysis']
)

top_issues_task = PythonOperator(
    task_id='analyze_top_return_issues',
    python_callable=top_issues_based_on_returns,
    dag=dag,
)