import dash
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
from sqlalchemy import create_engine
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dags.utils import config  # Make sure this points to your config file

# Database connection (REPLACE WITH YOUR ACTUAL CREDENTIALS)
DB_URI = f"postgresql://{config.DB_USERNAME}:{config.DB_PASSWORD}@{config.DB_HOSTNAME}:{config.DB_PORT_ID}/{config.DB_DATABASE_NAME}"
engine = create_engine(DB_URI)

try:
    with engine.connect() as conn:
        print("✅ Database connection successful!")
except Exception as e:
    print("❌ Database connection failed:", str(e))

# Fetch stock data
def fetch_data():
    query = "SELECT date, open, high, low, close, volume, symbol FROM stock_data;"  # Adjust query if needed
    with engine.connect() as conn:
        df = pd.read_sql(query, con=conn.connection)
    df["date"] = pd.to_datetime(df["date"])
    return df

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
df = fetch_data()
symbols = df["symbol"].unique()

# App Layout
app.layout = dbc.Container([
    html.H1("📈 Stock Market Dashboard", className="text-center text-light mb-4"),
    dcc.Dropdown(
        id="stock-dropdown",
        options=[{"label": symbol, "value": symbol} for symbol in symbols],
        value=[symbols[0]],
        multi=True,
        className="mb-3",
        style={
            "background-color": "#343a40",
            "color": "#ffffff"
        }
    ),
    dcc.RangeSlider(
        id='date-range-slider',
        min=df['date'].min().timestamp(),
        max=df['date'].max().timestamp(),
        value=[df['date'].min().timestamp(), df['date'].max().timestamp()],
        marks={
            int(ts): pd.to_datetime(ts, unit='s').strftime('%Y-%m-%d')
            for ts in np.linspace(df['date'].min().timestamp(), df['date'].max().timestamp(), num=10).astype(int)
        },
        step=None
    ),
    dbc.Row([
        dbc.Col(dcc.Graph(id="candlestick-chart"), width=12, lg=6),
        dbc.Col(dcc.Graph(id="macd-chart"), width=12, lg=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="moving-average-chart"), width=12, lg=6),
        dbc.Col(dcc.Graph(id="bollinger-bands-chart"), width=12, lg=6)
    ]),
], fluid=True)


# Callback to update charts
@app.callback(
    [Output("candlestick-chart", "figure"),
     Output("macd-chart", "figure"),
     Output("moving-average-chart", "figure"),
     Output("bollinger-bands-chart", "figure")],
    [Input("stock-dropdown", "value"),
     Input('date-range-slider', 'value')]
)
def update_charts(selected_stocks, date_range):
    filtered_df = df[df["symbol"].isin(selected_stocks)]

    # Date filtering
    start_date = pd.to_datetime(date_range[0], unit='s')
    end_date = pd.to_datetime(date_range[1], unit='s')
    filtered_df = filtered_df[(filtered_df['date'] >= start_date) & (filtered_df['date'] <= end_date)]

    # Candlestick Chart
    candlestick_fig = go.Figure()
    for stock in selected_stocks:
        stock_df = filtered_df[filtered_df["symbol"] == stock]
        candlestick_fig.add_trace(go.Candlestick(
            x=stock_df["date"], open=stock_df["open"], high=stock_df["high"],
            low=stock_df["low"], close=stock_df["close"], name=stock
        ))
    candlestick_fig.update_layout(title="Stock Price Candlestick Chart", template="plotly_dark")

    # MACD Chart
    macd_fig = go.Figure()
    for stock in selected_stocks:
        stock_df = filtered_df[filtered_df["symbol"] == stock].copy()
        stock_df['EMA12'] = stock_df['close'].ewm(span=12, adjust=False).mean()
        stock_df['EMA26'] = stock_df['close'].ewm(span=26, adjust=False).mean()
        stock_df['MACD'] = stock_df['EMA12'] - stock_df['EMA26']
        stock_df['Signal'] = stock_df['MACD'].ewm(span=9, adjust=False).mean()
        macd_fig.add_trace(go.Scatter(x=stock_df["date"], y=stock_df['MACD'], mode='lines', name=f"{stock} - MACD"))
        macd_fig.add_trace(go.Scatter(x=stock_df["date"], y=stock_df['Signal'], mode='lines', name=f"{stock} - Signal"))
    macd_fig.update_layout(title="MACD", template="plotly_dark")

    # Moving Average Line Chart
    ma_fig = go.Figure()
    for stock in selected_stocks:
        stock_df = filtered_df[filtered_df["symbol"] == stock].copy()
        stock_df["MA7"] = stock_df["close"].rolling(window=7).mean()
        ma_fig.add_trace(go.Scatter(x=stock_df["date"], y=stock_df["MA7"], mode='lines', name=f"{stock} - MA7"))
    ma_fig.update_layout(title="7-Day Moving Average", template="plotly_dark")

    # Bollinger Bands Chart
    bbands_fig = go.Figure()
    for stock in selected_stocks:
        stock_df = filtered_df[filtered_df["symbol"] == stock].copy()
        stock_df['MA20'] = stock_df['close'].rolling(window=20).mean()
        stock_df['SD20'] = stock_df['close'].rolling(window=20).std()
        stock_df['Upper'] = stock_df['MA20'] + 2 * stock_df['SD20']
        stock_df['Lower'] = stock_df['MA20'] - 2 * stock_df['SD20']
        bbands_fig.add_trace(go.Scatter(x=stock_df["date"], y=stock_df['Upper'], mode='lines', name=f"{stock} - Upper"))
        bbands_fig.add_trace(go.Scatter(x=stock_df["date"], y=stock_df['MA20'], mode='lines', name=f"{stock} - Middle"))
        bbands_fig.add_trace(go.Scatter(x=stock_df["date"], y=stock_df['Lower'], mode='lines', name=f"{stock} - Lower"))
    bbands_fig.update_layout(title="Bollinger Bands", template="plotly_dark")

    return candlestick_fig, macd_fig, ma_fig, bbands_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)