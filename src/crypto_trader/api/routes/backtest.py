"""
Backtest API Routes

Endpoints for running backtests and retrieving results.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from loguru import logger
import uuid

router = APIRouter()

# In-memory storage for backtest results (TODO: Replace with database)
backtest_jobs = {}


class BacktestRequest(BaseModel):
    """Request model for running a backtest."""
    strategy_name: str
    symbol: str
    timeframe: str = "1h"
    days: int = 90
    initial_capital: float = 10000.0
    commission: float = 0.001
    parameters: Dict[str, Any] = {}


class BacktestStatus(BaseModel):
    """Backtest job status."""
    job_id: str
    status: str  # pending, running, completed, failed
    progress: float = 0.0
    message: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class BacktestResult(BaseModel):
    """Backtest result model."""
    job_id: str
    strategy_name: str
    symbol: str
    timeframe: str
    metrics: Dict[str, Any]
    trades: List[Dict[str, Any]]
    equity_curve: List[Dict[str, Any]]


@router.post("/run", response_model=BacktestStatus)
async def run_backtest(
    request: BacktestRequest,
    background_tasks: BackgroundTasks
) -> BacktestStatus:
    """
    Start a new backtest run.

    This endpoint queues a backtest job and returns immediately.
    Use the job_id to check status and retrieve results.

    Request Body:
        strategy_name: Name of strategy to backtest
        symbol: Trading pair (e.g., BTC/USDT)
        timeframe: Candlestick timeframe (1m, 5m, 15m, 1h, 4h, 1d)
        days: Number of days of historical data
        initial_capital: Starting capital in USDT
        commission: Trading commission rate (default 0.1%)
        parameters: Strategy-specific parameters

    Returns:
        Job status with job_id for tracking
    """
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())

        # Create job status
        status = BacktestStatus(
            job_id=job_id,
            status="pending",
            message=f"Backtest queued for {request.strategy_name} on {request.symbol}",
            started_at=datetime.now()
        )

        # Store job
        backtest_jobs[job_id] = {
            "status": status,
            "request": request,
            "result": None
        }

        # Queue background task
        background_tasks.add_task(
            _run_backtest_task,
            job_id,
            request
        )

        logger.info(f"Backtest job {job_id} created for {request.strategy_name}")

        return status

    except Exception as e:
        logger.error(f"Error creating backtest job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/status", response_model=BacktestStatus)
async def get_backtest_status(job_id: str) -> BacktestStatus:
    """
    Get the status of a backtest job.

    Path Parameters:
        job_id: Unique job identifier

    Returns:
        Current job status and progress
    """
    if job_id not in backtest_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return backtest_jobs[job_id]["status"]


@router.get("/{job_id}/results", response_model=BacktestResult)
async def get_backtest_results(job_id: str) -> BacktestResult:
    """
    Get the results of a completed backtest.

    Path Parameters:
        job_id: Unique job identifier

    Returns:
        Backtest results with metrics, trades, and equity curve

    Raises:
        404: Job not found
        400: Job not yet completed
    """
    if job_id not in backtest_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job = backtest_jobs[job_id]

    if job["status"].status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job {job_id} is {job['status'].status}, not completed"
        )

    if job["result"] is None:
        raise HTTPException(status_code=500, detail="Results not available")

    return job["result"]


@router.get("/jobs", response_model=List[BacktestStatus])
async def list_backtest_jobs(limit: int = 50) -> List[BacktestStatus]:
    """
    List recent backtest jobs.

    Query Parameters:
        limit: Maximum number of jobs to return

    Returns:
        List of backtest job statuses
    """
    jobs = list(backtest_jobs.values())
    jobs.sort(key=lambda x: x["status"].started_at or datetime.min, reverse=True)
    return [j["status"] for j in jobs[:limit]]


async def _run_backtest_task(job_id: str, request: BacktestRequest):
    """
    Background task to run the actual backtest.

    This runs asynchronously and updates the job status.
    """
    try:
        from crypto_trader.strategies import get_registry
        from crypto_trader.data.fetchers import BinanceDataFetcher
        from crypto_trader.backtesting.engine import BacktestEngine
        from crypto_trader.core.config import BacktestConfig
        from datetime import timedelta

        # Update status
        backtest_jobs[job_id]["status"].status = "running"
        backtest_jobs[job_id]["status"].progress = 0.1
        backtest_jobs[job_id]["status"].message = "Loading strategy..."

        # Get strategy from registry
        registry = get_registry()
        if request.strategy_name not in registry:
            raise ValueError(f"Strategy '{request.strategy_name}' not found")

        strategy_class = registry[request.strategy_name]
        strategy = strategy_class()

        # Initialize strategy with parameters
        if request.parameters:
            strategy.initialize(request.parameters)

        # Update progress
        backtest_jobs[job_id]["status"].progress = 0.3
        backtest_jobs[job_id]["status"].message = "Fetching data..."

        # Fetch data
        fetcher = BinanceDataFetcher()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days)

        data = fetcher.get_ohlcv(
            symbol=request.symbol,
            timeframe=request.timeframe,
            start_date=start_date,
            end_date=end_date,
            limit=None
        )

        # Reset index to ensure 'timestamp' column exists for strategy validation
        data = data.reset_index()

        # Update progress
        backtest_jobs[job_id]["status"].progress = 0.5
        backtest_jobs[job_id]["status"].message = "Running backtest..."

        # Create backtest config
        config = BacktestConfig(
            initial_capital=request.initial_capital,
            commission=request.commission,
            slippage=0.0005
        )

        # Run backtest
        engine = BacktestEngine()
        result = engine.run_backtest(strategy, data, config)

        # Update progress
        backtest_jobs[job_id]["status"].progress = 0.9
        backtest_jobs[job_id]["status"].message = "Processing results..."

        # Format results
        backtest_result = BacktestResult(
            job_id=job_id,
            strategy_name=request.strategy_name,
            symbol=request.symbol,
            timeframe=request.timeframe,
            metrics={
                "total_return": result.metrics.total_return,
                "sharpe_ratio": result.metrics.sharpe_ratio,
                "max_drawdown": result.metrics.max_drawdown,
                "win_rate": result.metrics.win_rate,
                "total_trades": len(result.trades),
            },
            trades=[
                {
                    "timestamp": str(trade.entry_time),
                    "side": trade.side,
                    "price": trade.entry_price,
                    "pnl": trade.pnl,
                }
                for trade in result.trades[:100]  # Limit to first 100 trades
            ],
            equity_curve=[
                {
                    "timestamp": str(timestamp) if timestamp is not None else "",
                    "equity": float(value) if value is not None else 0.0,
                }
                for timestamp, value in result.equity_curve[:1000]  # Limit to 1000 points
            ]
        )

        # Mark as completed
        backtest_jobs[job_id]["status"].status = "completed"
        backtest_jobs[job_id]["status"].progress = 1.0
        backtest_jobs[job_id]["status"].message = "Backtest completed successfully"
        backtest_jobs[job_id]["status"].completed_at = datetime.now()
        backtest_jobs[job_id]["result"] = backtest_result

        logger.info(f"Backtest job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Backtest job {job_id} failed: {e}")
        backtest_jobs[job_id]["status"].status = "failed"
        backtest_jobs[job_id]["status"].message = f"Error: {str(e)}"
        backtest_jobs[job_id]["status"].completed_at = datetime.now()
