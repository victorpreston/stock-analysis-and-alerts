"""
## Stock Data Ingestion DAG

This DAG fetches stock market data from the Alpha Vantage API and uploads the results
to a Cloudflare bucket daily. The DAG consists of two tasks:

1. `fetch_data_task`: Fetches stock data for a given set of symbols and saves it locally.
2. `ingest_data_task`: Uploads the fetched data to Cloudflare storage.

The DAG uses Airflow's TaskFlow API to define dependencies and structure the workflow.
"""

import os
import csv
import boto3
import shutil
import requests

from dags.utils import config
from airflow.decorators import dag, task
from datetime import datetime, timedelta

@dag(
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"owner": "airflow", "retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["stock_data", "cloudflare"],
)
def stock_data_ingestion():
    @task
    def fetch_data(symbols: list) -> list:
        """Fetches stock data for given symbols and saves them as CSV files."""
        os.makedirs("temp", exist_ok=True)
        saved_files = []
        for symbol in symbols:
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={config.API_KEY}&outputsize=full'
            try:
                r = requests.get(url)
                r.raise_for_status()
                data = r.json()
                if "Time Series (Daily)" not in data:
                    print(f"Error: Unexpected API response for {symbol}: {data}")
                    continue
                filename = f'temp/{symbol}_data.csv'
                with open(filename, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
                    for date, stats in data['Time Series (Daily)'].items():
                        writer.writerow([
                            date,
                            stats['1. open'],
                            stats['2. high'],
                            stats['3. low'],
                            stats['4. close'],
                            stats['5. volume']
                        ])
                saved_files.append(filename)
            except requests.exceptions.RequestException as e:
                print(f"Request failed for {symbol}: {e}")
        return saved_files

    @task
    def ingest_data_to_cloudflare(files: list):
        """Uploads fetched data to a Cloudflare bucket."""
        s3 = boto3.client(
            service_name="s3",
            endpoint_url=config.CLOUDFLARE_API_URL,
            aws_access_key_id=config.CLOUDFLARE_ACCESS_KEY_ID,
            aws_secret_access_key=config.CLOUDFLARE_SECRET_ACCESS_KEY,
            region_name=config.REGION_NAME,
        )
        for file in files:
            with open(file, "rb") as f:
                # If the file is already in the bucket, it will be overwritten
                s3.upload_fileobj(f, config.CLOUDFLARE_BUCKET_NAME, os.path.basename(file))
                print(f"Uploaded {file} to {config.CLOUDFLARE_BUCKET_NAME}")
        shutil.rmtree('temp')

    symbols = config.symbols
    saved_files = fetch_data(symbols)
    ingest_data_to_cloudflare(saved_files)

stock_data_ingestion()
