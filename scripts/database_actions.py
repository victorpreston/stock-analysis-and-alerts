import io
import os
import config
import boto3
import psycopg2
import requests
import pandas as pd

from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
from pyspark.sql.types import StructType, StructField, StringType, LongType, DateType, FloatType

# Initialize S3 client
s3 = boto3.client(
    service_name="s3",
    endpoint_url=config.CLOUDFLARE_API_URL,
    aws_access_key_id=config.CLOUDFLARE_ACCESS_KEY_ID,
    aws_secret_access_key=config.CLOUDFLARE_SECRET_ACCESS_KEY,
    region_name=config.REGION_NAME,
)

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Stock Analysis") \
    .getOrCreate()

# PostgreSQL connection properties
db_url = config.DB_URL
db_properties = {
    "user": config.DB_PROPERTIES.get("user"),
    "password": config.DB_PROPERTIES.get("password"),
    "driver": config.DB_PROPERTIES.get("driver")
}

def pandas_dtype_to_spark_dtype(pandas_dtype):
    if pandas_dtype == 'int64':
        return LongType()
    elif pandas_dtype == 'float64':
        return FloatType()
    elif pandas_dtype == 'object':  # For strings
        return StringType()
    elif pandas_dtype == 'datetime64[ns]': # For dates
        return DateType()
    else:
        return StringType()

# Function to download files from Cloudflare
def download_file():
    fields = []
    client = boto3.client(
        service_name="s3",
        endpoint_url=config.CLOUDFLARE_API_URL,
        aws_access_key_id=config.CLOUDFLARE_ACCESS_KEY_ID,
        aws_secret_access_key=config.CLOUDFLARE_SECRET_ACCESS_KEY,
        region_name=config.REGION_NAME,
    )

    response = client.list_objects_v2(Bucket=config.CLOUDFLARE_BUCKET_NAME)

    # Merge all CSV files into a single DataFrame
    total_df = pd.DataFrame()

    for content in response['Contents']:
        obj_dict = client.get_object(Bucket=config.CLOUDFLARE_BUCKET_NAME, Key=content['Key'])
        
        # get the csv file
        csv_obj = obj_dict['Body'].read().decode('utf-8')
        csv_file = io.StringIO(csv_obj)
        df = pd.read_csv(csv_file)
        
        key = content['Key']
        filename = os.path.basename(key)  # Extract filename
        # Add Symbol Column (Example: from filename)
        symbol = filename.split("_")[0] if "_" in filename else filename.split(".")[0]
        df['Symbol'] = symbol

        total_df = pd.concat([
            total_df,
            df
        ])

    for col_name, dtype in total_df.dtypes.items():
        fields.append(StructField(col_name, pandas_dtype_to_spark_dtype(str(dtype)), True))
    schema = StructType(fields)

    return spark.createDataFrame(total_df, schema=schema)
        

# Write DataFrame to PostgreSQL
def write_to_postgresql(df, table_name, db_url, db_properties):
    df.write.jdbc(url=db_url, table=table_name, mode='append', properties=db_properties)

if __name__ == '__main__':
    total_df = download_file()
    total_df.tail(5)
    # Write data to PostgreSQL
    # write_to_postgresql(df, "stock_data", db_url, db_properties)

    # Stop Spark session
    spark.stop()
