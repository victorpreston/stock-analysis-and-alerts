import io
import os
import csv
import boto3
import config
import shutil
import requests

def fetch_data(symbol):
    """
    Fetches stock data for a given symbol from the Alpha Vantage API
    and saves it to a CSV file in the temp directory
    """
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={config.API_KEY}&outputsize=full'
    r = requests.get(url)
    data = r.json()
    
    if 'Time Series (Daily)' not in data:
        print("Error fetching data")
        return

    filename = f'{symbol}_data.csv'
    
    with open(f"temp/{filename}", mode='w', newline='') as file:
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
    
    print(f"Data saved to temp/{filename}")

def ingest_data_to_cloudflare():
    """
    Ingests the data in the temp directory to a cloudflare bucket
    """
    s3 = boto3.client(
        service_name ="s3",
        endpoint_url = config.CLOUDFARE_API_URL,
        aws_access_key_id = config.CLOUDFARE_ACCESS_KEY_ID,
        aws_secret_access_key = config.CLOUDFARE_SECRET_ACCESS_KEY,
        region_name = config.REGION_NAME,
    )
    for file in os.listdir('temp'):
        with open(os.path.join('temp', file), 'rb') as f:
            file_content = f.read()
            s3.upload_fileobj(io.BytesIO(file_content), config.CLOUFLARE_BUCKET_NAME, file)
            print(f"Uploaded {file} to {config.CLOUFLARE_BUCKET_NAME}")


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
