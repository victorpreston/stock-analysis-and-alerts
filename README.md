# Real-time Stock Price Analysis and Alerting

## Project Overview
This project provides a real-time stock price analysis and alerting system using the Alpha Vantage API. It fetches stock data, processes it with Python, stores it in a local PostgreSQL database, and sends email notifications when the stock price crosses user-defined thresholds.

## Features
- Real-time stock price retrieval using Alpha Vantage API
- Data processing and analysis with Python (Pandas)
- Storage of stock data in a PostgreSQL database
- Workflow orchestration with Apache Airflow
- Email alerts sent via Python’s `smtplib` or SendGrid

## Technologies Used
- **Programming Language**: Python
- **Data Ingestion**: `requests` (API calls)
- **Data Processing**: `Pandas` (data manipulation)
- **Data Storage**: PostgreSQL (local setup)
- **Workflow Orchestration**: Apache Airflow
- **Alerting**: Email notifications (via `smtplib` or SendGrid)

## Setup

### 1. Obtain an API Key
Create an account on [Alpha Vantage](https://www.alphavantage.co/) and obtain an API key to access real-time stock data.

### 2. Set Up the Virtual Environment
Follow the steps below to set up the virtual environment:

```bash
# Create a virtual environment
python -m venv venv

# For Windows users
./venv/Scripts/activate

# For Linux/Mac users
source venv/bin/activate
