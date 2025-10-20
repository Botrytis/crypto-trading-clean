"""
Walk-Forward Optimization System

Scientific approach to strategy validation and parameter optimization.
Prevents overfitting through proper train/validate/test splits.
"""

from crypto_trader.optimization.walk_forward import WalkForwardOptimizer
from crypto_trader.optimization.parameter_grid import ParameterGrid
from crypto_trader.optimization.splitter import DataSplitter

__all__ = [
    "WalkForwardOptimizer",
    "ParameterGrid",
    "DataSplitter",
]
