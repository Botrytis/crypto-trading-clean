"""
Automated Strategy Benchmarking Endpoints

Batch test all strategies across multiple timeframes, periods, and symbols.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
from loguru import logger

from crypto_trader.strategies import get_registry

router = APIRouter()

# In-memory storage for benchmark jobs (in production, use database)
benchmark_jobs: Dict[str, Dict[str, Any]] = {}


class BenchmarkConfig(BaseModel):
    """Configuration for automated benchmark run."""
    symbols: List[str] = Field(default=["BTC/USDT", "ETH/USDT"], description="Trading pairs to test")
    timeframes: List[str] = Field(default=["1h", "4h", "1d"], description="Timeframes to test")
    periods: List[int] = Field(default=[30, 90, 180], description="Historical periods in days")
    strategies: Optional[List[str]] = Field(default=None, description="Specific strategies to test (None = all)")
    initial_capital: float = Field(default=10000.0, description="Starting capital")
    commission: float = Field(default=0.001, description="Trading commission rate")


class BenchmarkStatus(BaseModel):
    """Status of a benchmark job."""
    job_id: str
    status: str  # pending, running, completed, failed
    progress: float = Field(ge=0.0, le=1.0)
    message: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_tests: int = 0
    completed_tests: int = 0
    failed_tests: int = 0


class BenchmarkResult(BaseModel):
    """Results from a completed benchmark."""
    job_id: str
    config: BenchmarkConfig
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]
    rankings: Dict[str, List[Dict[str, Any]]]
    started_at: datetime
    completed_at: datetime


@router.post("/run", response_model=BenchmarkStatus)
async def run_benchmark(config: BenchmarkConfig, background_tasks: BackgroundTasks):
    """
    Start automated benchmark comparing all strategies.

    This will test each strategy across all combinations of:
    - Symbols (e.g., BTC/USDT, ETH/USDT)
    - Timeframes (e.g., 1h, 4h, 1d)
    - Periods (e.g., 30, 90, 180 days)

    Returns job_id for tracking progress.
    """
    job_id = str(uuid.uuid4())

    # Get strategies to test
    registry = get_registry()
    all_strategies = list(registry.list_strategies().keys())

    if config.strategies:
        strategies_to_test = [s for s in config.strategies if s in all_strategies]
    else:
        strategies_to_test = all_strategies

    total_tests = len(strategies_to_test) * len(config.symbols) * len(config.timeframes) * len(config.periods)

    status = BenchmarkStatus(
        job_id=job_id,
        status="pending",
        progress=0.0,
        message=f"Queued {total_tests} tests ({len(strategies_to_test)} strategies × {len(config.symbols)} symbols × {len(config.timeframes)} timeframes × {len(config.periods)} periods)",
        started_at=datetime.now(),
        total_tests=total_tests,
        completed_tests=0,
        failed_tests=0
    )

    benchmark_jobs[job_id] = {
        "status": status,
        "config": config,
        "results": [],
        "strategies": strategies_to_test
    }

    # Run in background
    background_tasks.add_task(_run_benchmark_task, job_id, config, strategies_to_test)

    logger.info(f"Started benchmark job {job_id}: {total_tests} tests")

    return status


@router.get("/{job_id}/status", response_model=BenchmarkStatus)
async def get_benchmark_status(job_id: str):
    """Get status of a benchmark job."""
    if job_id not in benchmark_jobs:
        raise HTTPException(status_code=404, detail="Benchmark job not found")

    return benchmark_jobs[job_id]["status"]


@router.get("/{job_id}/results", response_model=BenchmarkResult)
async def get_benchmark_results(job_id: str):
    """Get results from a completed benchmark."""
    if job_id not in benchmark_jobs:
        raise HTTPException(status_code=404, detail="Benchmark job not found")

    job = benchmark_jobs[job_id]

    if job["status"].status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Benchmark not completed yet. Status: {job['status'].status}"
        )

    # Calculate summary and rankings
    results = job["results"]
    summary = _calculate_summary(results)
    rankings = _calculate_rankings(results)

    return BenchmarkResult(
        job_id=job_id,
        config=job["config"],
        results=results,
        summary=summary,
        rankings=rankings,
        started_at=job["status"].started_at,
        completed_at=job["status"].completed_at
    )


@router.get("/jobs", response_model=List[BenchmarkStatus])
async def list_benchmark_jobs(limit: int = 50):
    """List recent benchmark jobs."""
    jobs = sorted(
        benchmark_jobs.values(),
        key=lambda x: x["status"].started_at,
        reverse=True
    )
    return [j["status"] for j in jobs[:limit]]


async def _run_benchmark_task(job_id: str, config: BenchmarkConfig, strategies: List[str]):
    """Background task to run benchmark tests."""
    job = benchmark_jobs[job_id]
    status = job["status"]

    try:
        status.status = "running"
        status.message = "Running benchmark tests..."

        results = []
        completed = 0
        failed = 0
        total = len(strategies) * len(config.symbols) * len(config.timeframes) * len(config.periods)

        # Test each combination
        for strategy_name in strategies:
            for symbol in config.symbols:
                for timeframe in config.timeframes:
                    for period_days in config.periods:
                        try:
                            # Run single backtest
                            result = await _run_single_backtest(
                                strategy_name=strategy_name,
                                symbol=symbol,
                                timeframe=timeframe,
                                period_days=period_days,
                                initial_capital=config.initial_capital,
                                commission=config.commission
                            )

                            results.append(result)
                            completed += 1

                        except Exception as e:
                            logger.error(f"Backtest failed: {strategy_name} {symbol} {timeframe} {period_days}d - {e}")
                            failed += 1

                        # Update progress
                        status.completed_tests = completed
                        status.failed_tests = failed
                        status.progress = (completed + failed) / total
                        status.message = f"Testing {strategy_name} on {symbol} {timeframe} ({completed}/{total})"

        # Mark as completed
        status.status = "completed"
        status.progress = 1.0
        status.message = f"Completed {completed} tests ({failed} failed)"
        status.completed_at = datetime.now()
        job["results"] = results

        logger.info(f"Benchmark {job_id} completed: {completed} successful, {failed} failed")

    except Exception as e:
        status.status = "failed"
        status.message = f"Benchmark failed: {str(e)}"
        status.completed_at = datetime.now()
        logger.error(f"Benchmark {job_id} failed: {e}")


async def _run_single_backtest(
    strategy_name: str,
    symbol: str,
    timeframe: str,
    period_days: int,
    initial_capital: float,
    commission: float
) -> Dict[str, Any]:
    """Run a single backtest and return results."""
    # Mock implementation - replace with actual backtesting
    # This would integrate with the existing backtesting engine

    import random
    import time

    # Simulate backtest execution time
    await asyncio.sleep(random.uniform(0.1, 0.3))

    # Generate mock results (replace with real backtest)
    total_return = random.uniform(-0.3, 0.5)
    sharpe = random.uniform(-1.0, 3.0)
    max_dd = random.uniform(-0.5, -0.05)
    win_rate = random.uniform(0.3, 0.7)
    total_trades = random.randint(10, 200)

    return {
        "strategy": strategy_name,
        "symbol": symbol,
        "timeframe": timeframe,
        "period_days": period_days,
        "metrics": {
            "total_return": total_return,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd,
            "win_rate": win_rate,
            "total_trades": total_trades,
            "profit_factor": abs(total_return) / max(abs(max_dd), 0.01),
        },
        "timestamp": datetime.now().isoformat()
    }


def _calculate_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate summary statistics across all tests."""
    if not results:
        return {}

    total_tests = len(results)
    profitable = sum(1 for r in results if r["metrics"]["total_return"] > 0)

    avg_return = sum(r["metrics"]["total_return"] for r in results) / total_tests
    avg_sharpe = sum(r["metrics"]["sharpe_ratio"] for r in results) / total_tests
    avg_drawdown = sum(r["metrics"]["max_drawdown"] for r in results) / total_tests
    avg_win_rate = sum(r["metrics"]["win_rate"] for r in results) / total_tests

    return {
        "total_tests": total_tests,
        "profitable_tests": profitable,
        "profitability_rate": profitable / total_tests,
        "avg_return": avg_return,
        "avg_sharpe": avg_sharpe,
        "avg_drawdown": avg_drawdown,
        "avg_win_rate": avg_win_rate,
        "best_return": max(r["metrics"]["total_return"] for r in results),
        "worst_return": min(r["metrics"]["total_return"] for r in results),
    }


def _calculate_rankings(results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Calculate strategy rankings by different metrics."""

    # Group by strategy
    by_strategy = {}
    for result in results:
        strategy = result["strategy"]
        if strategy not in by_strategy:
            by_strategy[strategy] = []
        by_strategy[strategy].append(result)

    # Calculate average metrics per strategy
    strategy_stats = []
    for strategy, strategy_results in by_strategy.items():
        n = len(strategy_results)
        avg_metrics = {
            "strategy": strategy,
            "tests": n,
            "avg_return": sum(r["metrics"]["total_return"] for r in strategy_results) / n,
            "avg_sharpe": sum(r["metrics"]["sharpe_ratio"] for r in strategy_results) / n,
            "avg_drawdown": sum(r["metrics"]["max_drawdown"] for r in strategy_results) / n,
            "avg_win_rate": sum(r["metrics"]["win_rate"] for r in strategy_results) / n,
            "profitable_tests": sum(1 for r in strategy_results if r["metrics"]["total_return"] > 0),
            "profitability_rate": sum(1 for r in strategy_results if r["metrics"]["total_return"] > 0) / n
        }
        strategy_stats.append(avg_metrics)

    # Create rankings
    return {
        "by_return": sorted(strategy_stats, key=lambda x: x["avg_return"], reverse=True),
        "by_sharpe": sorted(strategy_stats, key=lambda x: x["avg_sharpe"], reverse=True),
        "by_drawdown": sorted(strategy_stats, key=lambda x: x["avg_drawdown"], reverse=True),
        "by_win_rate": sorted(strategy_stats, key=lambda x: x["avg_win_rate"], reverse=True),
        "by_consistency": sorted(strategy_stats, key=lambda x: x["profitability_rate"], reverse=True),
    }


# Add asyncio import at top of file
import asyncio
