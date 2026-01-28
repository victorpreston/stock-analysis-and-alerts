"""
Main FastAPI application for Stock Analysis and Alerts system
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.routes import stocks, alerts, watchlist, health

app = FastAPI(
    title="Stock Analysis and Alerts API",
    description="RESTful API for real-time stock analysis and alerting system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    print("Starting up Stock Analysis API...")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down Stock Analysis API...")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )


app.include_router(health.router, tags=["Health"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["Stocks"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["Watchlist"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Stock Analysis and Alerts API",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
