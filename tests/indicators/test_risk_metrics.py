"""
Tests for risk metrics
"""

import pytest
import pandas as pd
import numpy as np
from indicators.risk_metrics import RiskMetrics


class TestReturnsCalculation:
    """Test returns calculation"""
    
    def test_calculate_returns(self):
        """Test return calculation"""
        prices = pd.Series([100, 105, 110, 108, 112])
        returns = RiskMetrics.calculate_returns(prices)
        
        assert len(returns) == len(prices)
        assert returns.iloc[0] != returns.iloc[0]  # NaN for first value


class TestSharpeRatio:
    """Test Sharpe Ratio calculation"""
    
    def test_sharpe_ratio_positive_returns(self):
        """Test Sharpe ratio with positive returns"""
        returns = pd.Series([0.01, 0.02, 0.01, -0.01, 0.02] * 50)
        sharpe = RiskMetrics.sharpe_ratio(returns)
        
        assert isinstance(sharpe, float)
        assert sharpe > 0


class TestMaxDrawdown:
    """Test Maximum Drawdown calculation"""
    
    def test_max_drawdown_calculation(self):
        """Test max drawdown returns negative value"""
        prices = pd.Series([100, 110, 105, 95, 98, 102])
        drawdown = RiskMetrics.max_drawdown(prices)
        
        assert drawdown < 0
        assert drawdown >= -1


class TestVolatility:
    """Test volatility calculation"""
    
    def test_volatility_calculation(self):
        """Test volatility is positive"""
        returns = pd.Series(np.random.randn(252) * 0.01)
        volatility = RiskMetrics.volatility(returns)
        
        assert volatility >= 0


class TestCorrelationMatrix:
    """Test correlation matrix calculation"""
    
    def test_correlation_matrix_shape(self):
        """Test correlation matrix has correct shape"""
        prices = pd.DataFrame({
            'AAPL': np.random.rand(100) * 100 + 150,
            'GOOGL': np.random.rand(100) * 100 + 150,
            'MSFT': np.random.rand(100) * 100 + 150
        })
        
        corr = RiskMetrics.correlation_matrix(prices)
        
        assert corr.shape == (3, 3)
        assert (corr.iloc[0, 0] == 1.0)  # Correlation with self should be 1
