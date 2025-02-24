import dash
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash import dcc, html
from sqlalchemy import create_engine

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dags.utils import config


# PostgreSQL connection string (Update with your DB credentials)
DB_URI = f"postgresql://{config.DB_USERNAME}:{config.DB_PASSWORD}@{config.DB_HOSTNAME}:{config.DB_PORT_ID}/{config.DB_TABLE_NAME}"
engine = create_engine(DB_URI)

try:
    with engine.connect() as conn:
        print("✅ Database connection successful!")
        test_query = "SELECT 1;"
        result = conn.execute(test_query)
        print("✅ Test query executed:", result.fetchall())
except Exception as e:
    print("❌ Database connection failed:", str(e))

# Fetch stock data from PostgreSQL
def fetch_data():
    query = "SELECT date, open, high, low, close, volume, symbol FROM stock_data;"
    with engine.connect() as conn:
        df = pd.read_sql(
            sql=query,
            con=conn.connection
        )
    df["date"] = pd.to_datetime(df["date"])  # Convert date to datetime format
    return df

# Initialize Dash app
app = dash.Dash(__name__)
df = fetch_data()

# Get unique stock symbols
symbols = df["symbol"].unique()

# App Layout
app.layout = html.Div(children=[
    html.H1("Stock Market Dashboard"),
    
    # Dropdown for selecting stocks
    dcc.Dropdown(
        id="stock-dropdown",
        options=[{"label": symbol, "value": symbol} for symbol in symbols],
        value=[symbols[0]],  # Default selection
        multi=True  # Allow multiple stocks
    ),
    
    # Candlestick chart
    dcc.Graph(id="candlestick-chart"),

    # Volume bar chart
    dcc.Graph(id="volume-chart")
])

# Callback to update charts based on selected stocks
@app.callback(
    [dash.Output("candlestick-chart", "figure"),
     dash.Output("volume-chart", "figure")],
    [dash.Input("stock-dropdown", "value")]
)
def update_charts(selected_stocks):
    filtered_df = df[df["symbol"].isin(selected_stocks)]

    # Create Candlestick Chart
    candlestick_fig = go.Figure()
    for stock in selected_stocks:
        stock_df = filtered_df[filtered_df["symbol"] == stock]
        candlestick_fig.add_trace(go.Candlestick(
            x=stock_df["date"],
            open=stock_df["open"],
            high=stock_df["high"],
            low=stock_df["low"],
            close=stock_df["close"],
            name=stock
        ))
    candlestick_fig.update_layout(title="Stock Price Candlestick Chart", xaxis_title="Date", yaxis_title="Price")

    # Create Volume Bar Chart
    volume_fig = px.bar(filtered_df, x="date", y="volume", color="symbol", title="Trading Volume")

    return candlestick_fig, volume_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
