"""
Alert management endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services import DatabaseService, EmailAlertService
from api import schemas

router = APIRouter()
db = DatabaseService()
email_service = EmailAlertService()


@router.get("/", response_model=List[schemas.AlertResponse])
async def get_alerts(status: str = None):
    """Get all alerts, optionally filtered by status"""
    try:
        alerts = db.get_active_alerts()
        if status:
            alerts = alerts[alerts['status'] == status]
        return alerts.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{alert_id}", response_model=schemas.AlertResponse)
async def get_alert(alert_id: int):
    """Get specific alert by ID"""
    try:
        alerts = db.get_active_alerts()
        alert = alerts[alerts['id'] == alert_id]
        if alert.empty:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        return alert.iloc[0].to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=schemas.SuccessResponse)
async def create_alert(request: schemas.CreateAlertRequest):
    """Create new alert"""
    try:
        alert_id = db.create_alert(
            symbol=request.symbol,
            alert_type=request.alert_type,
            threshold_value=request.threshold_value,
            current_value=db.get_latest_price(request.symbol) or 0
        )
        return {
            'status': 'success',
            'message': f'Alert created successfully',
            'data': {'alert_id': alert_id}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{alert_id}", response_model=schemas.SuccessResponse)
async def update_alert(alert_id: int, request: schemas.UpdateAlertRequest):
    """Update alert status"""
    try:
        db.update_alert_status(alert_id, request.status)
        return {
            'status': 'success',
            'message': f'Alert {alert_id} updated to {request.status}'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{alert_id}", response_model=schemas.SuccessResponse)
async def delete_alert(alert_id: int):
    """Delete alert"""
    try:
        db.update_alert_status(alert_id, 'resolved')
        return {
            'status': 'success',
            'message': f'Alert {alert_id} deleted'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{alert_id}/test", response_model=schemas.SuccessResponse)
async def test_alert(alert_id: int, email: str):
    """Send test email for alert"""
    try:
        email_service.send_technical_alert(
            symbol='TEST',
            indicator='Test Alert',
            value=0.0,
            signal='This is a test',
            recipient_email=email
        )
        return {
            'status': 'success',
            'message': f'Test email sent to {email}'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/symbol/{symbol}", response_model=List[schemas.AlertResponse])
async def get_alerts_for_symbol(symbol: str):
    """Get all alerts for specific symbol"""
    try:
        alerts = db.get_active_alerts()
        symbol_alerts = alerts[alerts['symbol'] == symbol.upper()]
        return symbol_alerts.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
