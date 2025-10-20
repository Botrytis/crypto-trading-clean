# Walk-Forward Optimization System

The **scientific method** for strategy development. Prevents overfitting by testing on truly unseen data.

## Why Walk-Forward?

**The Problem:** Most people optimize strategies on historical data and think they've found gold. Then it fails in real trading.

**The Solution:** Split data into THREE parts:
- **Train (60%)**: Try all parameter combinations
- **Validation (20%)**: Pick the best parameters
- **Test (20%)**: Report final results (touched ONCE!)

If Test performance matches Validation, you have a robust strategy. If not, you're overfitting.

## Quick Start

```bash
# Optimize SMA Crossover on BTC
python scripts/walk_forward_optimize.py SMA_Crossover BTC/USDT 1d --days 180

# Output:
# Best Parameters:
#   fast_period: 20
#   slow_period: 100
#
# Performance (sharpe_ratio):
#   Train:      1.45
#   Validation: 1.32
#   Test:       1.28 ← Your expected future performance!
```

## How It Works

### 1. Data Split
```
|-------- Train (60%) --------|--- Val (20%) ---|--- Test (20%) ---|
        Optimize here          Select best here    Report once here
```

### 2. Optimization Process

```python
from crypto_trader.optimization import WalkForwardOptimizer
from crypto_trader.optimization.parameter_grid import create_sma_grid

# Create optimizer
optimizer = WalkForwardOptimizer(metric="sharpe_ratio")

# Define parameter grid
param_grid = create_sma_grid()  # 16 combinations

# Run optimization
result = optimizer.optimize(
    strategy_class=SMACrossoverStrategy,
    data=full_dataset,
    param_grid=param_grid,
    config=backtest_config
)

# Check results
print(f"Best params: {result.best_params}")
print(f"Test performance: {result.test_metric}")
```

### 3. Interpretation

**Good Result:**
```
Train:      1.45 sharpe
Validation: 1.42 sharpe  (within 5%)
Test:       1.38 sharpe  (within 5%)
```
→ Strategy generalizes well! Deploy it.

**Bad Result (Overfitting):**
```
Train:      2.10 sharpe
Validation: 1.35 sharpe  (35% drop!)
Test:       0.92 sharpe  (32% drop!)
```
→ Strategy memorized training data. Don't use it.

## Parameter Grids

Pre-defined grids for common strategies:

```python
from crypto_trader.optimization.parameter_grid import (
    create_sma_grid,      # SMA Crossover
    create_rsi_grid,      # RSI Mean Reversion
    create_bollinger_grid,# Bollinger Bands
    create_macd_grid      # MACD
)

# Or create custom grid
from crypto_trader.optimization import ParameterGrid

custom_grid = ParameterGrid({
    'fast_period': [10, 20, 30],
    'slow_period': [50, 100, 150],
    'threshold': [0.01, 0.02, 0.03]
})
# This creates 3 × 3 × 3 = 27 combinations
```

## Advanced: Walk-Forward Splits

For ultra-robust validation, use rolling windows:

```python
splitter = DataSplitter()

# Create 5 walk-forward periods
splits = splitter.walk_forward_splits(
    data=full_dataset,
    n_splits=5,
    test_size_pct=0.2
)

# Each split: Train on past, test on future
# Split 1: Train[0:100], Test[100:120]
# Split 2: Train[0:120], Test[120:140]
# Split 3: Train[0:140], Test[140:160]
# ...

# If strategy works on ALL 5 periods → Very robust!
```

## CLI Usage

```bash
# Basic optimization
python scripts/walk_forward_optimize.py SMA_Crossover BTC/USDT 1h --days 180

# Optimize for different metric
python scripts/walk_forward_optimize.py RSI_MeanReversion ETH/USDT 4h --metric total_return

# More capital and commission
python scripts/walk_forward_optimize.py MACD_Momentum BNB/USDT 1d --capital 50000 --commission 0.002
```

## Metrics to Optimize

Choose based on your goals:

- `sharpe_ratio` - Risk-adjusted returns (default, usually best)
- `total_return` - Raw profit (ignores risk)
- `max_drawdown` - Minimize losses (conservative)
- `win_rate` - Win percentage (can be misleading)

## Linus Torvalds Would Say:

"Talk is cheap. Show me the Test set results."

If your Test performance drops significantly from Validation, you're overfitting. Simple as that.

## Next Steps

1. Run walk-forward on your strategies
2. Compare Test results (not Train!)
3. Only deploy strategies with consistent Train→Val→Test performance
4. Re-optimize every 3-6 months with new data
