import os
import json

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

with open(CONFIG_PATH, "r") as f:
    config_data = json.load(f)

# Top 25 symbols from the S&P 500
symbols =  ["AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "FB", "TSLA", "BRK.B", "JPM", "JNJ", "V", "WMT", "PG", "MA", "UNH", "INTC", "HD", "VZ", "DIS", "NVDA", "ADBE", "CRM", "PYPL", "BAC", "NFLX"]
# Assign values to variables
API_KEY = config_data.get("API_KEY")
CLOUDFLARE_BUCKET_NAME = config_data.get("CLOUDFLARE_BUCKET_NAME")
CLOUDFLARE_API_URL = config_data.get("CLOUDFLARE_API_URL")
CLOUDFLARE_TOKEN_VALUE = config_data.get("CLOUDFLARE_TOKEN_VALUE")
CLOUDFLARE_ACCESS_KEY_ID = config_data.get("CLOUDFLARE_ACCESS_KEY_ID")
CLOUDFLARE_SECRET_ACCESS_KEY = config_data.get("CLOUDFLARE_SECRET_ACCESS_KEY")
REGION_NAME = config_data.get("REGION_NAME")

# PostgreSQL connection properties
DB_DATABASE = config_data.get("DB_DATABASE")
DB_HOSTNAME = config_data.get("DB_HOSTNAME")
DB_USERNAME = config_data.get("DB_USERNAME")
DB_PASSWORD = config_data.get("DB_PASSWORD")
DB_PORT_ID = config_data.get("DB_PORT_ID")
DB_TABLE_NAME = config_data.get("DB_TABLE_NAME")