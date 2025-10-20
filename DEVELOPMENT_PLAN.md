# Development Plan - Crypto Trading Framework

## Phase 1: Foundation (Week 1-2)

### 1.1 Core Data Layer
**Priority**: CRITICAL

- [ ] Clean data fetcher (keep ccxt integration)
- [ ] Implement proper caching (file-based, not Redis overkill)
- [ ] Data quality validation
  - Schema checks
  - Outlier detection  
  - Missing data handling
- [ ] Unit tests for data layer

**Files**:
```
src/crypto_trader/data/
├── __init__.py
├── fetcher.py          # Clean ccxt wrapper
├── cache.py            # Simple file cache
├── validator.py        # Data quality checks
└── types.py            # Data models (Pydantic)
```

### 1.2 Strategy Framework
**Priority**: CRITICAL

- [ ] Base strategy class (keep clean interface)
- [ ] Strategy registry (already good, just cleanup)
- [ ] Pick TOP 3 strategies from original:
  1. SMA Crossover (simple, works)
  2. RSI Mean Reversion (proven)
  3. Bollinger Breakout (volatility capture)
- [ ] Kill the rest (at least for v1)
- [ ] Unit tests per strategy

**Files**:
```
src/crypto_trader/strategies/
├── __init__.py
├── base.py             # BaseStrategy interface
├── registry.py         # Strategy registration
└── implementations/
    ├── sma_crossover.py
    ├── rsi_mean_reversion.py
    └── bollinger_breakout.py
```

### 1.3 Backtesting Engine
**Priority**: CRITICAL

- [ ] Extract core engine from monolith
- [ ] Clean separation of concerns
- [ ] Realistic transaction cost model
- [ ] Slippage modeling (market impact)
- [ ] Position tracking
- [ ] Unit tests + integration tests

**Files**:
```
src/crypto_trader/backtesting/
├── __init__.py
├── engine.py           # Core backtest loop
├── metrics.py          # Performance calculations
├── costs.py            # Transaction costs & slippage
└── reports.py          # Clean reporting
```

---

## Phase 2: Risk Management (Week 3)

### 2.1 Position Sizing
**Priority**: HIGH

- [ ] Kelly Criterion implementation
- [ ] Fixed fractional
- [ ] Volatility-adjusted sizing
- [ ] Maximum position limits
- [ ] Tests with edge cases

### 2.2 Portfolio Risk
**Priority**: HIGH

- [ ] Portfolio-level stop loss (actually enforced)
- [ ] Drawdown limits with circuit breakers
- [ ] Correlation-based position limits
- [ ] Risk budgeting
- [ ] Integration tests

**Files**:
```
src/crypto_trader/risk/
├── __init__.py
├── position_sizing.py
├── portfolio_limits.py
├── drawdown_control.py
└── validators.py
```

---

## Phase 3: Testing & Quality (Week 4)

### 3.1 Test Suite
**Priority**: HIGH

- [ ] Unit tests (>80% coverage)
- [ ] Integration tests (full pipeline)
- [ ] Property-based tests (hypothesis)
- [ ] Benchmark tests (performance regression)
- [ ] CI/CD setup (GitHub Actions)

### 3.2 Code Quality
**Priority**: MEDIUM

- [ ] Ruff linting (all files)
- [ ] Black formatting (consistent style)
- [ ] MyPy type checking
- [ ] Docstring coverage
- [ ] Pre-commit hooks

**Files**:
```
.github/workflows/
├── tests.yml
├── lint.yml
└── release.yml

tests/
├── unit/
├── integration/
├── fixtures/
└── conftest.py

.pre-commit-config.yaml
pyproject.toml
```

---

## Phase 4: CLI & Usability (Week 5)

### 4.1 Command Interface
**Priority**: MEDIUM

- [ ] Clean CLI with Typer
- [ ] Backtest command
- [ ] Optimize command  
- [ ] Validate-data command
- [ ] Report command
- [ ] Rich progress bars

### 4.2 Configuration
**Priority**: MEDIUM

- [ ] Single config file (YAML)
- [ ] Environment overrides
- [ ] Pydantic validation
- [ ] Config templates
- [ ] Migration guide from old configs

**Files**:
```
src/crypto_trader/cli/
├── __init__.py
├── backtest.py
├── optimize.py
├── validate.py
└── utils.py

config/
├── default.yaml
└── examples/
    ├── conservative.yaml
    ├── aggressive.yaml
    └── multi_asset.yaml
```

---

## Phase 5: Production Features (Week 6-8)

### 5.1 Monitoring & Observability
**Priority**: HIGH (for live trading)

- [ ] Structured logging (JSON format)
- [ ] Metrics collection (Prometheus format)
- [ ] Health checks
- [ ] Performance profiling
- [ ] Error tracking

### 5.2 Live Trading Foundation
**Priority**: MEDIUM (paper trading first!)

- [ ] Paper trading mode
- [ ] Order execution layer
- [ ] Fill tracking
- [ ] Position reconciliation
- [ ] Emergency stop mechanism

**Files**:
```
src/crypto_trader/execution/
├── __init__.py
├── broker.py           # Exchange interface
├── orders.py           # Order management
├── fills.py            # Fill tracking
└── reconcile.py        # Position reconciliation

src/crypto_trader/monitoring/
├── __init__.py
├── logger.py           # Structured logging
├── metrics.py          # Prometheus metrics
└── alerts.py           # Alert system
```

### 5.3 Data Pipeline Enhancement
**Priority**: MEDIUM

- [ ] Data versioning (simple, not DVC overkill)
- [ ] Incremental updates
- [ ] Multi-exchange support
- [ ] Graceful degradation
- [ ] Rate limiting & backoff

---

## Phase 6: Optimization (Week 9-10)

### 6.1 Performance
**Priority**: LOW (works first, fast second)

- [ ] Profile memory usage
- [ ] Consider Polars migration (if needed)
- [ ] Lazy loading for large datasets
- [ ] Parallel backtesting (keep from original)
- [ ] Benchmark suite

### 6.2 Advanced Features
**Priority**: LOW (nice to have)

- [ ] Walk-forward optimization (keep from original)
- [ ] Monte Carlo simulation
- [ ] Sensitivity analysis
- [ ] Strategy ensembles (if >3 strategies)

---

## What We're NOT Building (Yet)

❌ **Web dashboard** - CLI first, UI later
❌ **Database layer** - Files are fine for now  
❌ **Real-time streaming** - Batch processing works
❌ **Machine learning strategies** - Keep it simple
❌ **Multi-chain on-chain data** - Price data only
❌ **Sentiment analysis** - Noise, not signal
❌ **15+ strategies** - Focus on quality

---

## Success Metrics

### Phase 1-2 (MVP)
- [ ] Can backtest BTC/USDT with 3 strategies
- [ ] Realistic P&L (includes costs)
- [ ] Tests pass with >80% coverage
- [ ] No dependencies on unused libraries

### Phase 3-4 (Beta)
- [ ] CLI is intuitive
- [ ] Documentation is clear
- [ ] Others can run without handholding
- [ ] CI/CD pipeline working

### Phase 5-6 (Production)
- [ ] Paper trading works reliably
- [ ] Can run 24/7 without intervention
- [ ] Monitoring shows what's happening
- [ ] No surprises in live trading

---

## Resource Requirements

**Time**: ~10 weeks (one person, part-time)
**Skills needed**: Python, trading knowledge, systems design
**Infrastructure**: None (local dev sufficient)

---

## Migration from Original

For users of the original repo:

```bash
# Old way (bloated)
uv run python master.py --symbol BTC/USDT --quick

# New way (clean)
crypto-trader backtest --symbol BTC/USDT --strategy sma_cross --days 90
```

**Breaking changes**:
- 12 strategies removed (keep top 3)
- Config format changed (single YAML)
- Database/Redis removed (file cache)
- No more 20+ markdown docs (clean README + docs/)

**Migration guide**: TBD in docs/migration.md

---

## Review Checkpoints

**Week 2**: Foundation review
- Data layer works?
- Strategies ported correctly?
- Tests in place?

**Week 4**: Quality gate
- >80% coverage?
- Linting passes?
- CI/CD working?

**Week 6**: Beta release
- Can others use it?
- Docs clear?
- No major bugs?

**Week 10**: Production candidate
- Paper trading reliable?
- Monitoring working?
- Ready for real money?

---

## Open Questions

1. **Strategy selection**: Which 3 to keep? Need backtests on same data.
2. **Caching strategy**: File-based vs SQLite vs simple pickle?
3. **Configuration format**: YAML vs TOML vs Python?
4. **Deployment target**: Docker? Systemd? Kubernetes? (probably Docker)
5. **Monitoring stack**: Prometheus+Grafana? Or simpler?

---

## The Goal

**A crypto trading framework that professionals can actually use in production.**

- Clean code
- Well tested  
- Properly monitored
- Actually works with real money

**No academic bloat. No resume padding. Just solid engineering.**

Let's build this right.
