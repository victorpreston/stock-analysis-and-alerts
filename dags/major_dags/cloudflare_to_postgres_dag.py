"""
## Stock Data Processing DAG

This DAG downloads stock data files from Cloudflare storage, processes them into a Pandas DataFrame, and writes the results to a PostgreSQL database.

The DAG consists of two main tasks:

1. `download_data_task`: Downloads CSV files from Cloudflare and merges them into a Pandas DataFrame.
2. `write_to_postgresql_task`: Writes the processed DataFrame into a PostgreSQL database.

The DAG uses Airflow's TaskFlow API for structuring the workflow and handling dependencies.
"""

from airflow.decorators import dag, task
from datetime import datetime, timedelta
import io
import dags.utils.config as config
import boto3
import pandas as pd
from sqlalchemy import create_engine

@dag(
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"owner": "airflow", "retries": 1, "retry_delay": timedelta(minutes=5)},
    tags=["stock_data", "cloudflare", "postgres"],
)
def stock_data_processing():
    
    @task
    def download_data() -> pd.DataFrame:
        """Downloads stock data CSV files from Cloudflare and merges them into a Pandas DataFrame."""
        client = boto3.client(
            service_name="s3",
            endpoint_url=config.CLOUDFLARE_API_URL,
            aws_access_key_id=config.CLOUDFLARE_ACCESS_KEY_ID,
            aws_secret_access_key=config.CLOUDFLARE_SECRET_ACCESS_KEY,
            region_name=config.REGION_NAME,
        )
        
        response = client.list_objects_v2(Bucket=config.CLOUDFLARE_BUCKET_NAME)
        total_df = pd.DataFrame()
        
        for content in response.get('Contents', []):
            obj_dict = client.get_object(Bucket=config.CLOUDFLARE_BUCKET_NAME, Key=content['Key'])
            csv_obj = obj_dict['Body'].read().decode('utf-8')
            csv_file = io.StringIO(csv_obj)
            df = pd.read_csv(csv_file)
            
            filename = content['Key'].split("/")[-1]  # Extract filename from key
            symbol = filename.split("_")[0] if "_" in filename else filename.split(".")[0]
            df['Symbol'] = symbol  # Add stock symbol column
            
            total_df = pd.concat([total_df, df], ignore_index=True)
        
        return total_df

    @task
    def write_to_postgresql(total_df: pd.DataFrame):
        """Writes the merged DataFrame into a PostgreSQL database."""
        engine = create_engine(
            f"postgresql://{config.DB_USERNAME}:{config.DB_PASSWORD}@{config.DB_HOSTNAME}:{config.DB_PORT_ID}/{config.DB_DATABASE}"
        )
        
        with engine.connect() as conn:
            total_df.to_sql("stock_data", conn, if_exists="append", index=False)
            print(f"Inserted {len(total_df)} rows into stock_data")

    total_df = download_data()
    write_to_postgresql(total_df)
    
stock_data_processing()
