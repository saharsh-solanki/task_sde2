from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import json
import os
import re
from datetime import datetime
import subprocess
import sys

from utils.logging_utils import setup_logging
from configs.constants import Config

try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from nltk.corpus import stopwords
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk==3.8.1"])
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from nltk.corpus import stopwords

nltk.download("vader_lexicon")
nltk.download("stopwords")

sia = SentimentIntensityAnalyzer()
stop_words = set(stopwords.words("english"))

def clean_and_tokenize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    tokens = text.split()
    return [t for t in tokens if t not in stop_words]

def analyze_reviews(data):
    logger = setup_logging(log_dir=Config.LOGGER_INSIGHTS_DIR, log_file_prefix="top_issues_based_on_reviews")
    logger.info("Starting review analysis")
    
    try:
        with open(os.path.join(Config.SUGGESTION_DIR, "reviews.json"), "r") as suggestion_file:
            keyword_suggestions = json.load(suggestion_file)
        logger.info("Loaded {} keyword suggestions".format(len(keyword_suggestions)))

        suggestions = {}
        processed_count = 0

        for asin, details in data.items():
            most_negative_review = None
            lowest_score = 1

            for review in details.get("reviews", []):
                review_text = review["review_text"]
                sentiment = sia.polarity_scores(review_text)
                if sentiment["compound"] < lowest_score:
                    lowest_score = sentiment["compound"]
                    most_negative_review = review_text

            asin_suggestions = []

            if most_negative_review:
                tokens = clean_and_tokenize(most_negative_review)
                for token in tokens:
                    if token in keyword_suggestions:
                        asin_suggestions.append(keyword_suggestions[token])

            suggestions[asin] = {
                "most_negative_review": (
                    most_negative_review if most_negative_review else "N/A"
                ),
                "suggestions": list(set(asin_suggestions)),
            }
            processed_count += 1
            logger.debug("ASIN {}: Processed with {} suggestions".format(asin, len(asin_suggestions)))

        logger.info("Processed {} ASINs for review analysis".format(processed_count))
        return suggestions

    except Exception as e:
        logger.error("Error in review analysis: {}".format(str(e)))
        raise

def load_and_analyze_data():
    logger = setup_logging(log_dir=Config.LOGGER_INSIGHTS_DIR, log_file_prefix="top_issues_based_on_reviews")
    logger.info("Starting review-based insights analysis")
    
    try:
        logger.info("Loading merged data")
        with open(os.path.join(Config.OUTPUT_INGESTION_DIR, "merged_data.json"), "r") as file:
            data = json.load(file)
        logger.info("Loaded data for {} ASINs".format(len(data)))

        result = analyze_reviews(data=data)
        
        os.makedirs(Config.OUTPUT_INSIGHTS_DIR, exist_ok=True)
        
        output_path = os.path.join(Config.OUTPUT_INSIGHTS_DIR, "top_issues_based_on_reviews.json")
        logger.info("Saving results to {}".format(output_path))
        with open(output_path, "w") as outfile:
            json.dump(result, outfile, indent=4)
        
        logger.info("Output written to {}".format(output_path))
        logger.info("Review-based insights analysis completed successfully")
        return result

    except Exception as e:
        logger.error("Error in review-based insights analysis: {}".format(str(e)))
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
    'top_issues_based_on_reviews',
    default_args=default_args,
    description='Analyze top issues based on review sentiment and provide suggestions',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['insights', 'reviews-analysis']
)

analyze_reviews_task = PythonOperator(
    task_id='analyze_review_insights',
    python_callable=load_and_analyze_data,
    dag=dag,
)