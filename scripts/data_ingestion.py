import io
import os
import csv
import boto3
import config
import shutil
import requests

import requests
import csv
import config
import os

def fetch_data(symbol):
    """
    Fetches stock data for a given symbol from the Alpha Vantage API
    and saves it to a CSV file in the temp directory.
    """
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={config.API_KEY}&outputsize=full'
    
    try:
        r = requests.get(url)
        r.raise_for_status()  # Raise error if the request fails (e.g., network issues)
        data = r.json()
        
        # Check if the expected key is in the response
        if "Time Series (Daily)" not in data:
            print(f"Error: Unexpected API response for {symbol}: {data}")
            return
        
        # Ensure the temp directory exists
        os.makedirs("temp", exist_ok=True)
        
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
        
        print(f"Data saved to {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def ingest_data_to_cloudflare():
    """
    Ingests the data in the temp directory to a Cloudflare bucket
    """
    s3 = boto3.client(
        service_name="s3",
        endpoint_url=config.CLOUDFLARE_API_URL,
        aws_access_key_id=config.CLOUDFLARE_ACCESS_KEY_ID,
        aws_secret_access_key=config.CLOUDFLARE_SECRET_ACCESS_KEY,
        region_name=config.REGION_NAME,
    )

    temp_dir = os.path.join(os.getcwd(), "temp")

    for file in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, file)
        with open(file_path, "rb") as f:
            s3.upload_fileobj(f, config.CLOUDFLARE_BUCKET_NAME, file)
            print(f"Uploaded {file} to {config.CLOUDFLARE_BUCKET_NAME}")


if __name__ == '__main__':
    # Create temp directory
    if not os.path.exists('temp'):
        os.makedirs('temp')

    # Fetch data for each symbol
    for symbol in config.symbol_tickers:
        fetch_data(symbol)

    # Ingest data to cloudflare bucket
    ingest_data_to_cloudflare()

    # Clear the temp directory
    shutil.rmtree('temp')
