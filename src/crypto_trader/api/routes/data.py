"""
Data API Routes

Endpoints for market data, symbols, and timeframes.
"""

from typing import List, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

router = APIRouter()


class Symbol(BaseModel):
    """Trading symbol model."""
    symbol: str
    base: str
    quote: str
    exchange: str = "binance"


class Timeframe(BaseModel):
    """Timeframe model."""
    value: str
    label: str
    minutes: int


@router.get("/symbols", response_model=List[Symbol])
async def get_symbols() -> List[Symbol]:
    """
    Get list of available trading symbols.

    Returns:
        List of supported trading pairs
    """
    # TODO: Fetch from exchange dynamically
    # For now, return popular pairs
    symbols = [
        Symbol(symbol="BTC/USDT", base="BTC", quote="USDT"),
        Symbol(symbol="ETH/USDT", base="ETH", quote="USDT"),
        Symbol(symbol="BNB/USDT", base="BNB", quote="USDT"),
        Symbol(symbol="SOL/USDT", base="SOL", quote="USDT"),
        Symbol(symbol="ADA/USDT", base="ADA", quote="USDT"),
        Symbol(symbol="XRP/USDT", base="XRP", quote="USDT"),
        Symbol(symbol="DOT/USDT", base="DOT", quote="USDT"),
        Symbol(symbol="DOGE/USDT", base="DOGE", quote="USDT"),
        Symbol(symbol="AVAX/USDT", base="AVAX", quote="USDT"),
        Symbol(symbol="MATIC/USDT", base="MATIC", quote="USDT"),
    ]

    return symbols


@router.get("/timeframes", response_model=List[Timeframe])
async def get_timeframes() -> List[Timeframe]:
    """
    Get list of available timeframes.

    Returns:
        List of supported candlestick timeframes
    """
    timeframes = [
        Timeframe(value="1m", label="1 Minute", minutes=1),
        Timeframe(value="5m", label="5 Minutes", minutes=5),
        Timeframe(value="15m", label="15 Minutes", minutes=15),
        Timeframe(value="30m", label="30 Minutes", minutes=30),
        Timeframe(value="1h", label="1 Hour", minutes=60),
        Timeframe(value="4h", label="4 Hours", minutes=240),
        Timeframe(value="1d", label="1 Day", minutes=1440),
        Timeframe(value="1w", label="1 Week", minutes=10080),
    ]

    return timeframes


@router.get("/exchanges", response_model=List[str])
async def get_exchanges() -> List[str]:
    """
    Get list of supported exchanges.

    Returns:
        List of exchange names
    """
    # TODO: Expand to support multiple exchanges
    return ["binance"]
