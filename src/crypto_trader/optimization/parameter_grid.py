"""
Parameter Grid Search

Generate all combinations of strategy parameters for optimization.
"""

from typing import Dict, List, Any
from itertools import product
from loguru import logger


class ParameterGrid:
    """
    Generate parameter combinations for grid search.

    Examples:
        >>> grid = ParameterGrid({
        ...     'fast_period': [10, 20, 30],
        ...     'slow_period': [50, 100, 200]
        ... })
        >>> list(grid)
        [
            {'fast_period': 10, 'slow_period': 50},
            {'fast_period': 10, 'slow_period': 100},
            ...
        ]
    """

    def __init__(self, param_dict: Dict[str, List[Any]]):
        """
        Initialize parameter grid.

        Args:
            param_dict: Dictionary of parameter names to lists of values
        """
        self.param_dict = param_dict
        self._combinations = None

    def __iter__(self):
        """Iterate through all parameter combinations."""
        if self._combinations is None:
            self._generate_combinations()

        return iter(self._combinations)

    def __len__(self):
        """Get total number of combinations."""
        if self._combinations is None:
            self._generate_combinations()

        return len(self._combinations)

    def _generate_combinations(self):
        """Generate all combinations of parameters."""
        if not self.param_dict:
            self._combinations = [{}]
            return

        keys = list(self.param_dict.keys())
        values = [self.param_dict[k] for k in keys]

        self._combinations = []
        for combo in product(*values):
            self._combinations.append(dict(zip(keys, combo)))

        logger.info(f"Generated {len(self._combinations)} parameter combinations")

    def to_list(self) -> List[Dict[str, Any]]:
        """Return all combinations as a list."""
        return list(self)


def create_sma_grid() -> ParameterGrid:
    """
    Create parameter grid for SMA Crossover strategy.

    Returns:
        ParameterGrid with common SMA parameter combinations
    """
    return ParameterGrid({
        'fast_period': [5, 10, 20, 30],
        'slow_period': [50, 100, 150, 200]
    })


def create_rsi_grid() -> ParameterGrid:
    """
    Create parameter grid for RSI strategy.

    Returns:
        ParameterGrid with common RSI parameter combinations
    """
    return ParameterGrid({
        'period': [7, 14, 21, 28],
        'oversold': [20, 25, 30],
        'overbought': [70, 75, 80]
    })


def create_bollinger_grid() -> ParameterGrid:
    """
    Create parameter grid for Bollinger Bands strategy.

    Returns:
        ParameterGrid with common Bollinger parameter combinations
    """
    return ParameterGrid({
        'period': [10, 20, 30],
        'std_dev': [1.5, 2.0, 2.5, 3.0]
    })


def create_macd_grid() -> ParameterGrid:
    """
    Create parameter grid for MACD strategy.

    Returns:
        ParameterGrid with common MACD parameter combinations
    """
    return ParameterGrid({
        'fast_period': [8, 12, 16],
        'slow_period': [21, 26, 30],
        'signal_period': [7, 9, 11]
    })


# Registry of common parameter grids
PARAMETER_GRIDS = {
    'sma_crossover': create_sma_grid,
    'rsi_mean_reversion': create_rsi_grid,
    'bollinger_breakout': create_bollinger_grid,
    'macd_momentum': create_macd_grid,
}


def get_parameter_grid(strategy_name: str) -> ParameterGrid:
    """
    Get predefined parameter grid for a strategy.

    Args:
        strategy_name: Name of strategy (lowercase with underscores)

    Returns:
        ParameterGrid for the strategy

    Raises:
        KeyError: If strategy has no predefined grid
    """
    normalized_name = strategy_name.lower().replace('-', '_')

    if normalized_name not in PARAMETER_GRIDS:
        raise KeyError(f"No parameter grid defined for '{strategy_name}'")

    return PARAMETER_GRIDS[normalized_name]()
