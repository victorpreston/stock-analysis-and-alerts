"""
Stock data endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services import DatabaseService
from indicators import TechnicalIndicators, RiskMetrics
from utils.helpers import DataFormatter
from api import schemas

router = APIRouter()
db = DatabaseService()


@router.get("/", response_model=List[schemas.StockDataResponse])
async def get_all_stocks(limit: int = Query(100, ge=1, le=1000)):
    """Get all stocks with latest data"""
    try:
        symbols = db.get_all_symbols()
        results = []
        for symbol in symbols:
            df = db.get_stock_data(symbol, limit=1)
            if not df.empty:
                results.extend(df.to_dict('records'))
        return results[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}", response_model=schemas.StockDayChangeResponse)
async def get_stock(symbol: str):
    """Get stock current price and change"""
    try:
        df = db.get_stock_data(symbol.upper(), limit=2)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        latest = df.iloc[-1]
        previous = df.iloc[-2] if len(df) > 1 else latest
        
        change = latest['close'] - previous['close']
        change_percent = (change / previous['close']) if previous['close'] != 0 else 0
        
        return {
            'symbol': symbol.upper(),
            'current_price': float(latest['close']),
            'previous_close': float(previous['close']),
            'change': float(change),
            'change_percent': float(change_percent),
            'high': float(latest['high']),
            'low': float(latest['low']),
            'volume': int(latest['volume'])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/history", response_model=List[schemas.PriceHistoryResponse])
async def get_stock_history(symbol: str, limit: int = Query(100, ge=1, le=500)):
    """Get stock price history"""
    try:
        df = db.get_stock_data(symbol.upper(), limit=limit)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        df['change_percent'] = df['close'].pct_change()
        return df.to_dict('records')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/indicators", response_model=schemas.TechnicalIndicatorsResponse)
async def get_technical_indicators(symbol: str):
    """Get technical indicators for stock"""
    try:
        df = db.get_stock_data(symbol.upper(), limit=50)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        df = df.sort_values('date')
        latest_date = df['date'].iloc[-1]
        
        rsi = TechnicalIndicators.rsi(df['close'])
        macd_line, macd_signal, _ = TechnicalIndicators.macd(df['close'])
        upper_bb, middle_bb, lower_bb = TechnicalIndicators.bollinger_bands(df['close'])
        sma_20 = TechnicalIndicators.moving_average(df['close'], 20)
        sma_50 = TechnicalIndicators.moving_average(df['close'], 50)
        ema_12 = TechnicalIndicators.exponential_moving_average(df['close'], 12)
        
        return {
            'symbol': symbol.upper(),
            'date': latest_date,
            'rsi': float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None,
            'macd': float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else None,
            'macd_signal': float(macd_signal.iloc[-1]) if not pd.isna(macd_signal.iloc[-1]) else None,
            'bollinger_upper': float(upper_bb.iloc[-1]) if not pd.isna(upper_bb.iloc[-1]) else None,
            'bollinger_middle': float(middle_bb.iloc[-1]) if not pd.isna(middle_bb.iloc[-1]) else None,
            'bollinger_lower': float(lower_bb.iloc[-1]) if not pd.isna(lower_bb.iloc[-1]) else None,
            'sma_20': float(sma_20.iloc[-1]) if not pd.isna(sma_20.iloc[-1]) else None,
            'sma_50': float(sma_50.iloc[-1]) if not pd.isna(sma_50.iloc[-1]) else None,
            'ema_12': float(ema_12.iloc[-1]) if not pd.isna(ema_12.iloc[-1]) else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/risk-metrics", response_model=schemas.RiskMetricsResponse)
async def get_risk_metrics(symbol: str, period: int = Query(30, ge=5, le=365)):
    """Get risk metrics for stock"""
    try:
        df = db.get_stock_data(symbol.upper(), limit=period)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        prices = df['close']
        returns = RiskMetrics.calculate_returns(prices)
        
        return {
            'symbol': symbol.upper(),
            'volatility': float(RiskMetrics.volatility(returns)),
            'sharpe_ratio': float(RiskMetrics.sharpe_ratio(returns)),
            'max_drawdown': float(RiskMetrics.max_drawdown(prices)),
            'var_95': float(RiskMetrics.var_95(returns)),
            'cvar': float(RiskMetrics.cvar(returns)),
            'period_days': period
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/comparison")
async def compare_stocks(symbols: str = Query(..., description="Comma-separated symbols")):
    """Compare multiple stocks"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        results = {}
        
        for symbol in symbol_list:
            price = db.get_latest_price(symbol)
            if price:
                results[symbol] = {'current_price': price}
        
        if not results:
            raise HTTPException(status_code=404, detail="No valid symbols found")
        
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
