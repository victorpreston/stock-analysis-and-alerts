from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from scripts import data_ingestion as di

with DAG(
    dag_id="stock_analysis",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@hourly", # Or whatever interval you want
    catchup=False,
) as dag:
    fetch_data_task = PythonOperator(
        task_id="fetch_data",
        python_callable=di.run_ingestion,
        op_kwargs={"symbols": ['INTC', 'NVDA', 'AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA', 'FB', 'V', 'JPM']}, # Pass stock symbols
    )
    
    fetch_data_task