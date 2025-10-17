# Merch Tech Project For Analyzing Underperformance Of Products

This is a project that ingest the reviews, returns, and sales files in csv format and analyze the issue based on returns and reviews with suggestion.
This uses airflow to run the pipelines.

## Table of Contents

- [How to Setup](#how-to-setup)
- [How to Run](#how-to-run)
- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [DAGs Description](#dags-description)
- [Testing with Different Datasets](#testing-with-different-datasets)

## How to Setup

### Prerequisites

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Memory**: Minimum 4GB RAM
- **Storage**: Minimum 10GB free space
- **OS**: Linux, macOS, or Windows with WSL2

### Quick Setup (One Command)

1. **Clone**
   ```bash
   git clone https://github.com/saharsh-solanki/task_sde2.git
   cd sde2_task
   ```
2. **Setup project**
   <br/>
   Please run the below cmd to automatically set up the project (Make sure Docker is up and running before running the cmd).   
   ```bash
   ./build.sh
   ```

That's it! The script will automatically:
- Create necessary directories
- Set up Airflow user IDs
- Start all Docker services
- Initialize the database
- Make everything ready to use

### Manual Setup (Alternative)

If you prefer manual setup:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/saharsh-solanki/sde2_task.git
   cd sde2_task
   ```

2. **Create directories:**
   ```bash
   mkdir -p outputs/ingestion_files outputs/insights_files logs airflow_logs pipeline/db
   ```

3. **Set up Airflow user IDs:**
   ```bash
   echo "AIRFLOW_UID=$(id -u)" > .env
   echo "AIRFLOW_GID=0" >> .env
   ```

4. **Start services:**
    <br/>
   Before start the services please make sure your docker daemon is running.
   ```bash
   sudo docker compose up -d
   ```

6. **Wait for initialization (~2 minutes)**

## How to Run

### After Setup

Once you've run `sudo ./build.sh`, everything is ready! Just:

1. **Access Airflow UI:**
   - **URL**: http://localhost:8080
   - **Username**: `airflow`
   - **Password**: `airflow`

2. **Run the data ingestion pipeline:**
   - Find `data_pipeline` in the DAG list
   - Toggle it ON (switch to the right)
   - Click the Play button to trigger a manual run
   - Wait for it to complete (green checkmark )

3. **Run issue analysis pipeline DAGs:**
   - Enable `top_issues_based_on_returns` and run it
   - Enable `top_issues_based_on_reviews` and run it

4. **Monitor results:**
   - Check outputs in `outputs/` folder
   - View logs in `logs/` and `airflow_logs/`

### Stop Services

When you're done:
```bash
sudo docker compose down
```

### Restart Services

To start again:
```bash
sudo ./build.sh
```

## Project Overview

This project implements a complete data pipeline using Apache Airflow to first into single foramt than analyze based on given data:

1. **Ingest** e-commerce data (reviews, returns, sales)
2. **Process** and merge data from multiple sources
3. **Analyze** return patterns and review sentiments
4. **Generate** actionable business insights with suggestions

### Key Features

- **Docker-based deployment** for consistency
- **Custom logging** with organized log structure
- **Sentiment analysis** using NLTK
- **Automated insights** generation
- **Production-ready** configuration
- **Health checks** for reliable startup

## Project Structure

```
SDE2_TASK/
├── airflow_logs/
├── configs/
│   ├── __pycache__/
│   └── constants.py
├── inputs/
│   ├── returns/
│   │   ├── sde2_returns.csv
│   │   ├── test_returns_1_electronics.csv
│   │   ├── test_returns_2_fashion.csv
│   │   └── test_returns_3_home.csv
│   ├── reviews/
│   │   ├── sde2_reviews.csv
│   │   ├── test_reviews_1_electronics.csv
│   │   ├── test_reviews_2_fashion.csv
│   │   └── test_reviews_3_home.csv
│   └── sales/
│       ├── sde2_sales.csv
│       ├── test_sales_1_electronics.csv
│       ├── test_sales_2_fashion.csv
│       └── test_sales_3_home.csv
├── logs/
│   ├── ingestion/
│   │   └── data_pipeline_2025-10-16.log
│   └── insights/
│       ├── top_issues_based_on_returns_2025-10-16.log
│       └── top_issues_based_on_reviews_2025-10-16.log
├── outputs/
│   ├── ingestion_files/
│   │   └── merged_data.json
│   └── insights_files/
│       ├── top_issues_based_on_reviews.json
│       └── top_issues_based_on_returns.json
├── pipelines/
│   ├── analysis_pipelines/
│   │   ├── __pycache__/
│   │   ├── top_issues_based_on_returns.py
│   │   └── top_issues_based_on_reviews.py
│   ├── db/
│   └── ingestion_pipeline/
│       ├── __pycache__/
│       └── data_pipeline.py
├── suggestion_mappings/
│   ├── returns.json
│   └── reviews.json
├── utils/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── logging_utils.py
│   └── utils.py
├── .env
├── .gitignore
├── build.sh
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

## DAGs Description

### 1. Data Pipeline (`data_pipeline`)

**Purpose**: Ingests and merges data from multiple sources

**Tasks**:
- Load reviews data from CSV
- Load returns data from CSV  
- Load sales data from CSV
- Merge into unified JSON format

**Output**: `outputs/ingestion_files/merged_data.json`

### 2. Top Issues Based on Returns (`top_issues_based_on_returns`)

**Purpose**: Analyzes return patterns and provides suggestions

**Tasks**:
- Load merged data from previous DAG
- Identify top return reason per ASIN
- Map return reasons to suggestions
- Generate insights with actionable recommendations

**Output**: `outputs/insights_files/top_issues_based_on_returns.json`

**Dependencies**: Requires `data_pipeline` to complete first

### 3. Top Issues Based on Reviews (`top_issues_based_on_reviews`)

**Purpose**: Analyzes review sentiment and provides keyword-based suggestions

**Tasks**:
- Load merged data from previous DAG
- Perform sentiment analysis using NLTK
- Identify most negative reviews per ASIN
- Extract keywords and map to suggestions
- Generate insights with improvement recommendations

**Output**: `outputs/insights_files/top_issues_based_on_reviews.json`

**Dependencies**: Requires `data_pipeline` to complete first


## Testing with Different Datasets

### Dataset Format Requirements

Your CSV files must have these exact column names:

**Reviews Data (`sde2_reviews.csv`):**
```csv
asin,review_text,rating
ASIN-1000,"Great product",5
ASIN-1001,"Poor quality",2
```

**Returns Data (`sde2_returns.csv`):**
```csv
asin,return_reason,count
ASIN-1000,Defective product,5
ASIN-1001,Late delivery,3
```

**Sales Data (`sde2_sales.csv`):**
```csv
asin,week,units_sold,gmv,refunds
ASIN-1000,1,100,5000,200
ASIN-1001,1,50,2500,100
```

### Testing Steps

1. **Replace your data files** in the `inputs/` directory:
   ```bash
   cp your_reviews.csv inputs/reviews/your_reviews.csv
   cp your_returns.csv inputs/returns/your_returns.csv
   cp your_sales.csv inputs/sales/your_sales.csv
   ```

2. **Update file paths in DAGs** (if using different filenames):
   
   Edit `airflow/dags/dag1_data_pipeline.py` and change these lines:
   ```python
   # Change these file paths to match your data files
   with open(os.path.join(REVIEW_DATA_DIR, "your_reviews.csv"), "r", encoding="utf-8") as f:
   with open(os.path.join(RETURN_DATA_DIR, "your_returns.csv"), "r", encoding="utf-8") as f:
   with open(os.path.join(SALES_DATA_DIR, "your_sales.csv"), "r", encoding="utf-8") as f:
   ```

3. **Run the pipeline**:
   ```bash
   ./build.sh
   ```

4. **Check results**:
   ```bash
   cat outputs/ingestion_files/merged_data.json
   cat outputs/insights_files/top_issues_based_on_returns.json
   cat outputs/insights_files/top_issues_based_on_reviews.json
   ```

### Quick Test with Sample Data

```bash
# Create minimal test data
echo "asin,review_text,rating
TEST-001,Great product,5
TEST-002,Poor quality,2" > inputs/reviews/sde2_reviews.csv

echo "asin,return_reason,count
TEST-001,Defective product,2
TEST-002,Late delivery,1" >inputs/returns/sde2_returns.csv

echo "asin,week,units_sold,gmv,refunds
TEST-001,1,50,2500,100
TEST-002,1,25,1250,50" > inputs/sales/sde2_sales.csv
```  

**Last Updated**: October 16, 2025  
**Status**: Production Ready
