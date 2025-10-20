"""
FastAPI Application - Main Entry Point

This module sets up the FastAPI application with all routes, middleware,
and configuration for the crypto trading platform API.

Usage:
    uvicorn crypto_trader.api.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from crypto_trader.api.routes import strategies, backtest, data

# Create FastAPI app
app = FastAPI(
    title="Crypto Trading Platform API",
    description="REST API for strategy research, backtesting, and analysis",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(strategies.router, prefix="/api/strategies", tags=["strategies"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["backtest"])
app.include_router(data.router, prefix="/api/data", tags=["data"])


@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    logger.info("🚀 Crypto Trading API starting up...")
    logger.info("📊 Loading strategies...")
    logger.info("✅ API ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    logger.info("👋 Crypto Trading API shutting down...")


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "Crypto Trading Platform API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/api/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
