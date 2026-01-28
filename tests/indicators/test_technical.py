"""
Tests for technical indicators
"""

import pytest
import pandas as pd
import numpy as np
from indicators.technical import TechnicalIndicators


class TestMovingAverage:
    """Test Simple Moving Average calculations"""
    
    def test_sma_calculation(self):
        """Test SMA returns correct values"""
        data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        result = TechnicalIndicators.moving_average(data, period=3)
        
        expected = pd.Series([np.nan, np.nan, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
        pd.testing.assert_series_equal(result, expected)
    
    def test_ema_calculation(self):
        """Test EMA returns correct values"""
        data = pd.Series([1, 2, 3, 4, 5])
        result = TechnicalIndicators.exponential_moving_average(data, period=2)
        
        assert len(result) == len(data)
        assert result.iloc[-1] > result.iloc[0]  # EMA should trend upward


class TestRSI:
    """Test Relative Strength Index"""
    
    def test_rsi_returns_valid_range(self):
        """Test RSI returns values between 0-100"""
        data = pd.Series(np.random.rand(100) * 100 + 50)
        result = TechnicalIndicators.rsi(data, period=14)
        
        valid_values = result.dropna()
        assert (valid_values >= 0).all() and (valid_values <= 100).all()


class TestMACD:
    """Test MACD calculation"""
    
    def test_macd_returns_three_series(self):
        """Test MACD returns macd_line, signal_line, and histogram"""
        data = pd.Series(np.random.rand(100) * 100 + 50)
        macd_line, signal_line, histogram = TechnicalIndicators.macd(data)
        
        assert len(macd_line) == len(data)
        assert len(signal_line) == len(data)
        assert len(histogram) == len(data)


class TestBollingerBands:
    """Test Bollinger Bands calculation"""
    
    def test_bb_returns_three_bands(self):
        """Test Bollinger Bands returns upper, middle, lower bands"""
        data = pd.Series(np.random.rand(100) * 100 + 50)
        upper, middle, lower = TechnicalIndicators.bollinger_bands(data)
        
        assert (upper >= middle).all()
        assert (lower <= middle).all()
        assert (upper >= lower).all()
