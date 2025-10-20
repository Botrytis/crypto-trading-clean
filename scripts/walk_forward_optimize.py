#!/usr/bin/env python3
"""
Walk-Forward Optimization CLI

Usage:
    python scripts/walk_forward_optimize.py SMA_Crossover BTC/USDT 1h --days 180

Example output:
    Phase 1: Optimizing on training data (108 days)...
      Tested 16 parameter combinations
      Best train sharpe: 1.45

    Phase 2: Validating on validation data (36 days)...
      Best val sharpe: 1.32

    Phase 3: Final test on unseen data (36 days)...
      Test sharpe: 1.28 ✓

    Best parameters:
      fast_period: 20
      slow_period: 100

    Performance:
      Train:  1.45 sharpe, 15.3% return
      Val:    1.32 sharpe, 12.8% return
      Test:   1.28 sharpe, 11.5% return ← This is your expected future performance!
"""

import sys
import argparse
from datetime import datetime, timedelta
from loguru import logger

from crypto_trader.strategies import get_registry
from crypto_trader.data.fetchers import BinanceDataFetcher
from crypto_trader.optimization import WalkForwardOptimizer
from crypto_trader.optimization.parameter_grid import get_parameter_grid, ParameterGrid
from crypto_trader.core.config import BacktestConfig

# Load strategy library
import crypto_trader.strategies.library  # noqa: F401


def main():
    parser = argparse.ArgumentParser(
        description="Walk-forward parameter optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument("strategy", help="Strategy name (e.g., SMA_Crossover)")
    parser.add_argument("symbol", help="Trading pair (e.g., BTC/USDT)")
    parser.add_argument("timeframe", help="Timeframe (e.g., 1h, 4h, 1d)")
    parser.add_argument("--days", type=int, default=180, help="Days of history to use")
    parser.add_argument("--metric", default="sharpe_ratio", help="Metric to optimize")
    parser.add_argument("--capital", type=float, default=10000, help="Initial capital")
    parser.add_argument("--commission", type=float, default=0.001, help="Commission rate")

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Walk-Forward Optimization")
    logger.info("=" * 60)

    # Get strategy
    registry = get_registry()
    strategies = registry.list_strategies()

    if args.strategy not in strategies:
        logger.error(f"Strategy '{args.strategy}' not found")
        logger.info(f"Available: {', '.join(strategies.keys())}")
        sys.exit(1)

    strategy_class = strategies[args.strategy]["class"]
    logger.info(f"Strategy: {args.strategy}")

    # Get parameter grid
    try:
        param_grid = get_parameter_grid(args.strategy.lower())
        logger.info(f"Parameter grid: {len(param_grid)} combinations")
    except KeyError:
        logger.error(f"No parameter grid defined for {args.strategy}")
        logger.info("Available grids: SMA_Crossover, RSI_MeanReversion, BollingerBreakout, MACD_Momentum")
        sys.exit(1)

    # Fetch data
    logger.info(f"Fetching {args.days} days of {args.symbol} {args.timeframe}...")
    fetcher = BinanceDataFetcher()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)

    data = fetcher.get_ohlcv(
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=start_date,
        end_date=end_date
    )

    # Reset index for strategy validation
    data = data.reset_index()

    logger.info(f"Loaded {len(data)} bars")
    logger.info(f"Date range: {data['timestamp'].min()} to {data['timestamp'].max()}")

    # Create backtest config
    config = BacktestConfig(
        initial_capital=args.capital,
        commission=args.commission,
        slippage=0.0005
    )

    # Run walk-forward optimization
    optimizer = WalkForwardOptimizer(metric=args.metric)

    result = optimizer.optimize(
        strategy_class=strategy_class,
        data=data,
        param_grid=param_grid,
        config=config
    )

    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    print("\nBest Parameters:")
    for key, value in result.best_params.items():
        print(f"  {key}: {value}")

    print(f"\nPerformance ({args.metric}):")
    print(f"  Train:      {result.train_metric:.4f}")
    print(f"  Validation: {result.val_metric:.4f}")
    if result.test_metric:
        print(f"  Test:       {result.test_metric:.4f} ← Expected future performance")

        # Check for overfitting
        train_val_diff = abs(result.train_metric - result.val_metric) / result.train_metric
        val_test_diff = abs(result.val_metric - result.test_metric) / result.val_metric

        print("\nOverfitting Check:")
        print(f"  Train→Val degradation:  {train_val_diff:.1%}")
        print(f"  Val→Test degradation:   {val_test_diff:.1%}")

        if val_test_diff < 0.1:
            print("  Status: ✓ Good generalization")
        elif val_test_diff < 0.25:
            print("  Status: ⚠ Moderate overfitting")
        else:
            print("  Status: ✗ Significant overfitting")

    # Top 5 parameter combinations
    print("\nTop 5 Parameter Combinations (by validation):")
    sorted_results = sorted(result.all_results, key=lambda x: x['metric'], reverse=True)
    for i, r in enumerate(sorted_results[:5], 1):
        print(f"  {i}. {args.metric}={r['metric']:.4f}, return={r['total_return']:.2%}, params={r['params']}")

    print("\n" + "=" * 60)
    logger.success("Optimization complete!")


if __name__ == "__main__":
    main()
