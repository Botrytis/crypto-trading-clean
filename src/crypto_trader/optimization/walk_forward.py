"""
Walk-Forward Optimization

The scientific method for strategy validation.
Prevents overfitting by testing on truly unseen data.

Process:
1. Split data: Train (60%) | Validation (20%) | Test (20%)
2. Optimize parameters on Train data
3. Select best parameters using Validation data
4. Report final results on Test data (touched only once!)

This ensures the Test results represent real future performance.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from loguru import logger

from crypto_trader.optimization.splitter import DataSplitter
from crypto_trader.optimization.parameter_grid import ParameterGrid
from crypto_trader.backtesting.engine import BacktestEngine
from crypto_trader.core.config import BacktestConfig


@dataclass
class OptimizationResult:
    """Results from parameter optimization."""
    best_params: Dict[str, Any]
    best_metric: float
    all_results: List[Dict[str, Any]]
    train_metric: float
    val_metric: float
    test_metric: Optional[float] = None


class WalkForwardOptimizer:
    """
    Walk-forward optimizer with train/val/test splits.

    Implements the scientific method for strategy development:
    1. Explore on Train
    2. Select on Validation
    3. Report on Test (once!)
    """

    def __init__(
        self,
        metric: str = "sharpe_ratio",
        train_pct: float = 0.6,
        val_pct: float = 0.2,
        test_pct: float = 0.2
    ):
        """
        Initialize walk-forward optimizer.

        Args:
            metric: Metric to optimize ('sharpe_ratio', 'total_return', etc.)
            train_pct: Training set percentage
            val_pct: Validation set percentage
            test_pct: Test set percentage
        """
        self.metric = metric
        self.splitter = DataSplitter(train_pct, val_pct, test_pct)
        self.engine = BacktestEngine()

        logger.info(f"WalkForwardOptimizer initialized (metric={metric})")

    def optimize(
        self,
        strategy_class: type,
        data: pd.DataFrame,
        param_grid: ParameterGrid,
        config: BacktestConfig
    ) -> OptimizationResult:
        """
        Run full walk-forward optimization.

        Args:
            strategy_class: Strategy class to optimize
            data: Full dataset
            param_grid: Parameter combinations to test
            config: Backtest configuration

        Returns:
            OptimizationResult with best parameters and performance
        """
        logger.info(f"Starting walk-forward optimization for {strategy_class.__name__}")
        logger.info(f"  Testing {len(param_grid)} parameter combinations")
        logger.info(f"  Dataset: {len(data)} rows")

        # Split data
        train_data, val_data, test_data = self.splitter.split(data)

        # Phase 1: Optimize on Training data
        logger.info("Phase 1: Optimizing on training data...")
        train_results = self._test_parameters(
            strategy_class, train_data, param_grid, config
        )

        if not train_results:
            raise ValueError("No valid results from training optimization")

        # Phase 2: Validate on Validation data
        logger.info("Phase 2: Validating on validation data...")
        val_results = self._test_parameters(
            strategy_class, val_data, param_grid, config
        )

        # Find best parameters based on validation performance
        best_idx = self._get_best_index(val_results)
        best_params = val_results[best_idx]['params']
        best_val_metric = val_results[best_idx]['metric']

        logger.info(f"Best parameters selected: {best_params}")
        logger.info(f"  Train metric: {train_results[best_idx]['metric']:.4f}")
        logger.info(f"  Val metric: {best_val_metric:.4f}")

        # Phase 3: Test on Test data (ONLY ONCE!)
        logger.info("Phase 3: Final test on unseen test data...")
        test_result = self._test_single(
            strategy_class, test_data, best_params, config
        )

        if test_result:
            logger.success(f"Test metric: {test_result['metric']:.4f}")

        return OptimizationResult(
            best_params=best_params,
            best_metric=best_val_metric,
            all_results=val_results,
            train_metric=train_results[best_idx]['metric'],
            val_metric=best_val_metric,
            test_metric=test_result['metric'] if test_result else None
        )

    def _test_parameters(
        self,
        strategy_class: type,
        data: pd.DataFrame,
        param_grid: ParameterGrid,
        config: BacktestConfig
    ) -> List[Dict[str, Any]]:
        """
        Test all parameter combinations on a dataset.

        Args:
            strategy_class: Strategy class
            data: Data to test on
            param_grid: Parameters to test
            config: Backtest configuration

        Returns:
            List of results for each parameter combination
        """
        results = []

        for i, params in enumerate(param_grid):
            result = self._test_single(strategy_class, data, params, config)

            if result:
                results.append(result)

            if (i + 1) % 10 == 0:
                logger.debug(f"  Tested {i + 1}/{len(param_grid)} combinations")

        logger.info(f"  Completed {len(results)}/{len(param_grid)} valid tests")
        return results

    def _test_single(
        self,
        strategy_class: type,
        data: pd.DataFrame,
        params: Dict[str, Any],
        config: BacktestConfig
    ) -> Optional[Dict[str, Any]]:
        """
        Test a single parameter combination.

        Args:
            strategy_class: Strategy class
            data: Data to test on
            params: Strategy parameters
            config: Backtest configuration

        Returns:
            Dict with results or None if failed
        """
        try:
            # Instantiate strategy with parameters
            strategy = strategy_class(**params)

            # Run backtest
            result = self.engine.run_backtest(strategy, data, config)

            # Extract metric
            metric_value = getattr(result.metrics, self.metric, None)

            if metric_value is None:
                logger.warning(f"Metric '{self.metric}' not found in results")
                return None

            return {
                'params': params,
                'metric': float(metric_value),
                'total_return': result.metrics.total_return,
                'sharpe_ratio': result.metrics.sharpe_ratio,
                'max_drawdown': result.metrics.max_drawdown,
                'total_trades': len(result.trades),
                'win_rate': result.metrics.win_rate
            }

        except Exception as e:
            logger.debug(f"Test failed for params {params}: {e}")
            return None

    def _get_best_index(self, results: List[Dict[str, Any]]) -> int:
        """
        Find index of best result based on metric.

        Args:
            results: List of test results

        Returns:
            Index of best result
        """
        if not results:
            raise ValueError("No results to find best from")

        # For most metrics, higher is better
        # For drawdown, lower is better
        if self.metric == 'max_drawdown':
            return min(range(len(results)), key=lambda i: abs(results[i]['metric']))
        else:
            return max(range(len(results)), key=lambda i: results[i]['metric'])
