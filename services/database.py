"""
Database service layer for CRUD operations
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import pandas as pd
from typing import List, Optional
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dags.utils import config
from models.stock import StockData, Alert, UserWatchlist, Base


class DatabaseService:
    """
    Service class for all database operations
    """
    
    def __init__(self):
        self.db_uri = f"postgresql://{config.DB_USERNAME}:{config.DB_PASSWORD}@{config.DB_HOSTNAME}:{config.DB_PORT_ID}/{config.DB_DATABASE_NAME}"
        self.engine = create_engine(self.db_uri)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables if they don't exist"""
        Base.metadata.create_all(self.engine)
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def get_stock_data(self, symbol: str, limit: int = 100) -> pd.DataFrame:
        """Fetch stock data for a symbol"""
        with self.get_session() as session:
            query = session.query(StockData).filter(
                StockData.symbol == symbol.upper()
            ).order_by(StockData.date.desc()).limit(limit)
            
            data = pd.read_sql(query.statement, self.engine)
            return data.sort_values('date')
    
    def get_all_symbols(self) -> List[str]:
        """Get all unique stock symbols in database"""
        with self.get_session() as session:
            symbols = session.query(StockData.symbol).distinct().all()
            return [s[0] for s in symbols]
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get the latest close price for a symbol"""
        with self.get_session() as session:
            latest = session.query(StockData).filter(
                StockData.symbol == symbol.upper()
            ).order_by(StockData.date.desc()).first()
            
            return float(latest.close) if latest else None
    
    def insert_stock_data(self, data: pd.DataFrame):
        """Insert stock data into database"""
        with self.get_session() as session:
            for _, row in data.iterrows():
                stock_entry = StockData(
                    symbol=row['symbol'].upper(),
                    date=row['date'],
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=int(row['volume'])
                )
                session.add(stock_entry)
    
    def create_alert(self, symbol: str, alert_type: str, 
                    threshold_value: float, current_value: float) -> int:
        """Create a new alert"""
        with self.get_session() as session:
            alert = Alert(
                symbol=symbol.upper(),
                alert_type=alert_type,
                threshold_value=threshold_value,
                current_value=current_value,
                status='active'
            )
            session.add(alert)
            session.flush()
            return alert.id
    
    def get_active_alerts(self) -> pd.DataFrame:
        """Get all active alerts"""
        with self.get_session() as session:
            query = session.query(Alert).filter(Alert.status == 'active')
            return pd.read_sql(query.statement, self.engine)
    
    def update_alert_status(self, alert_id: int, status: str):
        """Update alert status"""
        with self.get_session() as session:
            alert = session.query(Alert).filter(Alert.id == alert_id).first()
            if alert:
                alert.status = status
    
    def add_to_watchlist(self, user_id: str, symbol: str):
        """Add symbol to user watchlist"""
        with self.get_session() as session:
            watchlist = UserWatchlist(
                user_id=user_id,
                symbol=symbol.upper()
            )
            session.add(watchlist)
    
    def get_user_watchlist(self, user_id: str) -> List[str]:
        """Get user's watchlist"""
        with self.get_session() as session:
            symbols = session.query(UserWatchlist.symbol).filter(
                UserWatchlist.user_id == user_id
            ).all()
            return [s[0] for s in symbols]
    
    def remove_from_watchlist(self, user_id: str, symbol: str):
        """Remove symbol from user watchlist"""
        with self.get_session() as session:
            session.query(UserWatchlist).filter(
                UserWatchlist.user_id == user_id,
                UserWatchlist.symbol == symbol.upper()
            ).delete()
