import json

# Load config.json
with open("config.json", "r") as f:
    config_data = json.load(f)

# Assign values to variables
API_KEY = config_data.get("API_KEY")
CLOUDFLARE_BUCKET_NAME = config_data.get("CLOUDFLARE_BUCKET_NAME")
CLOUDFLARE_API_URL = config_data.get("CLOUDFLARE_API_URL")
CLOUDFLARE_TOKEN_VALUE = config_data.get("CLOUDFLARE_TOKEN_VALUE")
CLOUDFLARE_ACCESS_KEY_ID = config_data.get("CLOUDFLARE_ACCESS_KEY_ID")
CLOUDFLARE_SECRET_ACCESS_KEY = config_data.get("CLOUDFLARE_SECRET_ACCESS_KEY")
REGION_NAME = config_data.get("REGION_NAME")

# PostgreSQL connection properties
DB_URL = config_data.get("db_url")
DB_PROPERTIES = {
    "user": config_data.get("user"),
    "password": config_data.get("password"),
    "driver": config_data.get("driver")
}