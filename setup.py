from setuptools import setup, find_packages

setup(
    name="stock-analysis-alerts",
    version="1.0.0",
    description="Real-time stock price analysis and alerting system",
    author="Victor Preston",
    author_email="prestonvictor25@gmail.com",
    packages=find_packages(),
    python_requires=">=3.12",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "pandas>=2.0.0",
        "numpy>=2.0.0",
        "requests>=2.31.0",
        "plotly>=5.0.0",
        "dash>=2.14.0",
        "dash-bootstrap-components>=1.4.0",
        "apache-airflow>=2.10.0",
        "boto3>=1.28.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
            "pylint>=2.17.0",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
