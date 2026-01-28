"""
Health check and system status endpoints
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services import DatabaseService
from api import schemas

router = APIRouter()
db = DatabaseService()


@router.get("/health", response_model=schemas.HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        db_status = "connected"
        try:
            symbols = db.get_all_symbols()
        except:
            db_status = "error"
        
        return {
            'status': 'healthy' if db_status == 'connected' else 'unhealthy',
            'database': db_status,
            'api_version': '1.0.0',
            'timestamp': datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def system_status():
    """Get system status"""
    try:
        symbols = db.get_all_symbols()
        return {
            'status': 'operational',
            'total_symbols': len(symbols),
            'database': 'connected',
            'timestamp': datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
