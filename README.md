# Crypto Trading Framework - Clean Fork

**Original**: https://github.com/dedigadot/Crypto-Multi-Pair  
**This Fork**: Stripped down, production-focused cryptocurrency backtesting

## What We Kept

- Core backtesting engine
- Strategy registry pattern  
- Data fetching with caching
- Walk-forward validation
- Parallel processing

## What We Removed

- 70% of unused dependencies
- Academic "SOTA 2025" bloat
- Duplicate backup files
- 20+ markdown bug reports
- Unused database/cache layers

## What We Added

- Real risk management
- Proper testing suite
- Clean architecture
- Production monitoring
- Data quality checks

## Philosophy

**No bullshit. Just code that works.**

- 3-5 robust strategies > 15 half-baked ones
- Tested > Documented
- Simple > Clever
- Working > Perfect

## Quick Start

```bash
# Install core dependencies only
pip install -r requirements.txt

# Run a backtest
python -m crypto_trader backtest --symbol BTC/USDT --strategy sma_cross --days 365

# Run tests
pytest

# Check data quality
python -m crypto_trader validate-data
```

## Architecture

```
src/crypto_trader/
├── data/          # Fetch, cache, validate
├── strategies/    # 3-5 battle-tested strategies
├── backtesting/   # Core engine
├── risk/          # Actual risk management
├── execution/     # Live trading (paper mode first)
└── cli/           # Clean command interface
```

## Core Principles

1. **Measure twice, cut once**: Profile before optimizing
2. **Test everything**: No untested code in main
3. **Fail fast**: Validate inputs, handle errors
4. **Simple wins**: Complexity is the enemy

## Status

🚧 **Under active development**

- [x] Analysis of original codebase
- [ ] Core refactoring
- [ ] Test suite
- [ ] Risk management
- [ ] Production deployment

## Contributing

PRs welcome. Requirements:
- Tests included
- Documented (code comments + docstrings)
- Linted (ruff)
- Formatted (black)

**Delete before you add.**

## License

MIT (same as original)

---

*Built by people who actually trade, not just backtest.*
