"""
Risk management and performance calculations
"""

import pandas as pd
import numpy as np


class RiskMetrics:
    """
    Calculate risk and performance metrics for portfolios and stocks
    """
    
    @staticmethod
    def calculate_returns(prices: pd.Series, periods: int = 1) -> pd.Series:
        """Calculate percentage returns"""
        return prices.pct_change(periods=periods)
    
    @staticmethod
    def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe Ratio
        Measures risk-adjusted returns
        """
        excess_returns = returns.mean() - (risk_free_rate / 252)
        volatility = returns.std() * np.sqrt(252)
        
        if volatility == 0:
            return 0
        return excess_returns / volatility
    
    @staticmethod
    def max_drawdown(prices: pd.Series) -> float:
        """
        Calculate Maximum Drawdown
        Shows peak-to-trough decline
        """
        cumulative = (1 + prices.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    @staticmethod
    def var_95(returns: pd.Series) -> float:
        """
        Calculate Value at Risk (95% confidence)
        Maximum loss expected 95% of the time
        """
        return returns.quantile(0.05)
    
    @staticmethod
    def cvar(returns: pd.Series, confidence: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR)
        Average loss when returns fall below VAR
        """
        var = returns.quantile(1 - confidence)
        return returns[returns <= var].mean()
    
    @staticmethod
    def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sortino Ratio
        Like Sharpe but only penalizes downside volatility
        """
        excess_returns = returns.mean() - (risk_free_rate / 252)
        downside_returns = returns[returns < 0]
        downside_volatility = downside_returns.std() * np.sqrt(252)
        
        if downside_volatility == 0:
            return 0
        return excess_returns / downside_volatility
    
    @staticmethod
    def calmar_ratio(returns: pd.Series) -> float:
        """
        Calculate Calmar Ratio
        Annual return / Max drawdown
        """
        annual_return = returns.mean() * 252
        max_dd = RiskMetrics.max_drawdown(pd.Series((1 + returns).cumprod()))
        
        if abs(max_dd) < 0.0001:
            return 0
        return annual_return / abs(max_dd)
    
    @staticmethod
    def volatility(returns: pd.Series, periods: int = 252) -> float:
        """
        Calculate annualized volatility
        """
        return returns.std() * np.sqrt(periods)
    
    @staticmethod
    def correlation_matrix(price_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate correlation matrix for multiple assets
        """
        returns = price_data.pct_change().dropna()
        return returns.corr()
    
    @staticmethod
    def beta(asset_returns: pd.Series, market_returns: pd.Series) -> float:
        """
        Calculate Beta
        Measure of asset volatility relative to market
        """
        covariance = asset_returns.cov(market_returns)
        market_variance = market_returns.var()
        
        if market_variance == 0:
            return 0
        return covariance / market_variance
