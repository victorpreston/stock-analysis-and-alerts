"""
Utility functions for data validation and formatting
"""

import pandas as pd
from datetime import datetime
from typing import Optional, Tuple


class DataValidator:
    """
    Validation functions for stock data
    """
    
    @staticmethod
    def validate_stock_data(df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate stock data integrity
        Returns: (is_valid, message)
        """
        required_columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']
        
        if not all(col in df.columns for col in required_columns):
            return False, f"Missing required columns. Expected: {required_columns}"
        
        if df.empty:
            return False, "DataFrame is empty"
        
        if (df['close'] <= 0).any() or (df['volume'] < 0).any():
            return False, "Invalid values detected (negative prices or volume)"
        
        if (df['high'] < df['low']).any() or (df['high'] < df['close']).any():
            return False, "High price cannot be less than low or close price"
        
        return True, "Data validation passed"
    
    @staticmethod
    def check_missing_data(df: pd.DataFrame) -> pd.Series:
        """Check for missing values in dataset"""
        return df.isnull().sum()
    
    @staticmethod
    def check_outliers(df: pd.DataFrame, column: str, std_threshold: float = 3.0) -> pd.DataFrame:
        """
        Detect outliers using standard deviation
        Returns rows that are outliers
        """
        mean = df[column].mean()
        std = df[column].std()
        
        outliers = df[abs(df[column] - mean) > std_threshold * std]
        return outliers
    
    @staticmethod
    def check_price_gaps(df: pd.DataFrame, threshold: float = 0.1) -> pd.DataFrame:
        """
        Detect price gaps
        threshold: percentage change (e.g., 0.1 = 10%)
        """
        df = df.sort_values('date')
        df['price_change'] = df['close'].pct_change()
        gaps = df[abs(df['price_change']) > threshold]
        return gaps
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate records"""
        return df.drop_duplicates(subset=['symbol', 'date'])


class DataFormatter:
    """
    Format and transform data for display
    """
    
    @staticmethod
    def format_currency(value: float, decimal_places: int = 2) -> str:
        """Format value as currency"""
        return f"${value:,.{decimal_places}f}"
    
    @staticmethod
    def format_percentage(value: float, decimal_places: int = 2) -> str:
        """Format value as percentage"""
        return f"{value * 100:.{decimal_places}f}%"
    
    @staticmethod
    def format_large_number(value: int) -> str:
        """Format large numbers with K, M, B suffix"""
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.2f}K"
        else:
            return str(value)
    
    @staticmethod
    def format_date(date_obj, format_string: str = "%Y-%m-%d") -> str:
        """Format datetime object"""
        if isinstance(date_obj, str):
            date_obj = pd.to_datetime(date_obj)
        return date_obj.strftime(format_string)
    
    @staticmethod
    def round_to_nearest(value: float, nearest: float = 0.01) -> float:
        """Round value to nearest specified amount"""
        return round(value / nearest) * nearest


class CalculationHelper:
    """
    Helper functions for common calculations
    """
    
    @staticmethod
    def percent_change(old_value: float, new_value: float) -> float:
        """Calculate percentage change"""
        if old_value == 0:
            return 0
        return ((new_value - old_value) / abs(old_value))
    
    @staticmethod
    def absolute_change(old_value: float, new_value: float) -> float:
        """Calculate absolute change"""
        return new_value - old_value
    
    @staticmethod
    def calculate_pivot_points(high: float, low: float, close: float) -> dict:
        """
        Calculate pivot points for trading
        Used to identify support and resistance levels
        """
        pivot = (high + low + close) / 3
        r1 = (2 * pivot) - low
        r2 = pivot + (high - low)
        s1 = (2 * pivot) - high
        s2 = pivot - (high - low)
        
        return {
            'pivot': pivot,
            'resistance_1': r1,
            'resistance_2': r2,
            'support_1': s1,
            'support_2': s2
        }
    
    @staticmethod
    def calculate_vwap(high: float, low: float, close: float, volume: int, 
                      cumulative_volume: int) -> float:
        """
        Calculate Volume Weighted Average Price
        """
        typical_price = (high + low + close) / 3
        return (typical_price * volume) / cumulative_volume
