#!/bin/bash

echo "Setting up Airflow Data Pipeline Project..."

# Stop and remove any existing containers
echo "Stopping and removing existing Docker containers..."
sudo docker compose down --volumes --remove-orphans

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p outputs/ingestion_files outputs/insights_files logs airflow_logs pipelines/db


echo "AIRFLOW_UID=$(id -u)" > .env
echo "AIRFLOW_GID=0" >> .env


echo "Starting Airflow services with Docker Compose..."
sudo docker compose up -d

# Wait for services to initialize
echo "Waiting for Airflow services to initialize (this may take a minute or two)..."
sleep 60


echo "Airflow services status:"
sudo docker compose ps

# Wait a bit more for scheduler to be ready
echo "Waiting for scheduler to be ready..."
sleep 30

echo "Note: You can trigger DAGs manually through the Airflow UI"

echo "Airflow setup complete! Access the UI at http://localhost:8080 (user: airflow, pass: airflow)"
echo "You can monitor logs in the 'logs/' and 'airflow_logs/' directories."
