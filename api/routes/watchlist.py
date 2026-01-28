"""
Watchlist management endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services import DatabaseService
from api import schemas

router = APIRouter()
db = DatabaseService()


@router.get("/{user_id}", response_model=List[schemas.WatchlistItemResponse])
async def get_watchlist(user_id: str):
    """Get user watchlist"""
    try:
        symbols = db.get_user_watchlist(user_id)
        if not symbols:
            return []
        
        results = []
        for symbol in symbols:
            price = db.get_latest_price(symbol)
            results.append({
                'user_id': user_id,
                'symbol': symbol,
                'current_price': price,
                'created_at': None  # Would need to enhance database to track this
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=schemas.SuccessResponse)
async def add_to_watchlist(request: schemas.AddToWatchlistRequest):
    """Add symbol to watchlist"""
    try:
        existing = db.get_user_watchlist(request.user_id)
        if request.symbol.upper() in existing:
            raise HTTPException(status_code=400, detail=f"{request.symbol} already in watchlist")
        
        db.add_to_watchlist(request.user_id, request.symbol)
        return {
            'status': 'success',
            'message': f'{request.symbol} added to watchlist'
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/{symbol}", response_model=schemas.SuccessResponse)
async def remove_from_watchlist(user_id: str, symbol: str):
    """Remove symbol from watchlist"""
    try:
        db.remove_from_watchlist(user_id, symbol)
        return {
            'status': 'success',
            'message': f'{symbol} removed from watchlist'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/count")
async def get_watchlist_count(user_id: str):
    """Get watchlist item count"""
    try:
        symbols = db.get_user_watchlist(user_id)
        return {'user_id': user_id, 'count': len(symbols)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
