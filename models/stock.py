"""
Stock data models and schema definitions for PostgreSQL
"""

from sqlalchemy import Column, String, Float, DateTime, Integer, Numeric
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class StockData(Base):
    """
    ORM model for stock_data table
    """
    __tablename__ = "stock_data"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<StockData(symbol='{self.symbol}', date='{self.date}', close={self.close})>"


class Alert(Base):
    """
    ORM model for alerts table
    """
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, index=True)
    alert_type = Column(String(20), nullable=False)  # 'price_threshold', 'volume_spike', etc.
    threshold_value = Column(Numeric(10, 2), nullable=False)
    current_value = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default='active')  # 'active', 'triggered', 'resolved'
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Alert(symbol='{self.symbol}', type='{self.alert_type}', status='{self.status}')>"


class UserWatchlist(Base):
    """
    ORM model for user watchlists
    """
    __tablename__ = "user_watchlist"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False, index=True)
    symbol = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserWatchlist(user='{self.user_id}', symbol='{self.symbol}')>"
