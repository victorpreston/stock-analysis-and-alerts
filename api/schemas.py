"""
Request and response schemas for API
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class StockDataResponse(BaseModel):
    """Stock data response model"""
    symbol: str
    date: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: int = Field(..., ge=0)
    
    class Config:
        from_attributes = True


class StockDayChangeResponse(BaseModel):
    """Stock with day change calculation"""
    symbol: str
    current_price: float
    previous_close: float
    change: float
    change_percent: float
    high: float
    low: float
    volume: int


class TechnicalIndicatorsResponse(BaseModel):
    """Technical indicators response"""
    symbol: str
    date: datetime
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_12: Optional[float] = None


class AlertResponse(BaseModel):
    """Alert response model"""
    id: int
    symbol: str
    alert_type: str
    threshold_value: float
    current_value: float
    status: str
    created_at: datetime
    triggered_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CreateAlertRequest(BaseModel):
    """Create alert request"""
    symbol: str
    alert_type: str = Field(..., description="price_threshold, volume_spike, etc.")
    threshold_value: float = Field(..., gt=0)
    notification_email: Optional[str] = None


class UpdateAlertRequest(BaseModel):
    """Update alert request"""
    status: str = Field(..., description="active, triggered, resolved")


class WatchlistItemResponse(BaseModel):
    """Watchlist item response"""
    user_id: str
    symbol: str
    created_at: datetime
    current_price: Optional[float] = None
    change_percent: Optional[float] = None
    
    class Config:
        from_attributes = True


class AddToWatchlistRequest(BaseModel):
    """Add to watchlist request"""
    user_id: str
    symbol: str


class RiskMetricsResponse(BaseModel):
    """Risk metrics response"""
    symbol: str
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    var_95: float
    cvar: float
    period_days: int


class PriceHistoryResponse(BaseModel):
    """Price history response"""
    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    change_percent: Optional[float] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = "error"
    detail: str
    code: int


class SuccessResponse(BaseModel):
    """Generic success response"""
    status: str = "success"
    message: str
    data: Optional[dict] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    api_version: str
    timestamp: datetime
