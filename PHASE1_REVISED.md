# Phase 1 (Revised) - Strategy Research Platform

## Mission
Build a **strategy research and comparison platform** with web UI, not a minimal production trading bot.

## Core Goals
1. **Keep & expand strategies** - Add more, don't remove
2. **Web UI first** - Interactive dashboard for strategy comparison
3. **Clean architecture** - Make it easy to add new strategies
4. **Data quality** - Reliable backtesting requires good data

---

## Week 1: Foundation & Data Quality

### 1.1 Data Layer Enhancement ⭐ CRITICAL
**Priority**: HIGH - Everything depends on good data

**Tasks**:
- [x] Audit existing data fetchers (`src/crypto_trader/data/`)
- [ ] Add data validation layer
  - Schema checks (OHLCV format)
  - Outlier detection (flash crashes, data gaps)
  - Missing data handling
- [ ] Improve caching mechanism
  - Check current implementation
  - Add cache invalidation
  - Cache hit/miss logging
- [ ] Multi-exchange support preparation
  - Currently only Binance
  - Abstract exchange interface
- [ ] Data quality metrics dashboard
  - Show data coverage
  - Highlight gaps/issues

**Files to create**:
```
src/crypto_trader/data/
├── validators.py       # Data quality checks
├── cache_manager.py    # Better caching
├── exchange_base.py    # Abstract exchange
└── quality_metrics.py  # Data health monitoring
```

**Success metric**: Can fetch clean data for any symbol, see quality metrics

---

### 1.2 Strategy Infrastructure ⭐ CRITICAL
**Priority**: HIGH - Make it easy to add strategies

**Current state**: Good! Strategy registry pattern works well.

**Tasks**:
- [x] Audit strategy base class (`src/crypto_trader/strategies/base.py`)
- [ ] Add strategy metadata system
  - Tags (trend-following, mean-reversion, ML, etc.)
  - Complexity rating
  - Recommended timeframes
  - Parameter ranges
- [ ] Strategy testing framework
  - Smoke tests for all strategies
  - Parameter validation
  - Signal generation checks
- [ ] Strategy comparison utilities
  - Side-by-side metrics
  - Statistical significance tests
  - Correlation analysis

**Files to create**:
```
src/crypto_trader/strategies/
├── metadata.py         # Strategy metadata
├── testing.py          # Strategy test harness
└── comparison.py       # Compare multiple strategies
```

**Success metric**: Can add new strategy in <50 lines of code, auto-tested

---

### 1.3 Backtesting Engine Audit
**Priority**: MEDIUM - Current engine works, but verify quality

**Tasks**:
- [ ] Review engine implementation (`src/crypto_trader/backtesting/engine.py`)
- [ ] Add detailed logging
  - Every trade logged
  - Capital snapshots
  - Error tracking
- [ ] Improve cost modeling
  - Maker/taker fees
  - Slippage based on volume
  - Market impact (for large orders)
- [ ] Portfolio-level backtesting
  - Multi-strategy allocation
  - Rebalancing costs
  - Correlation tracking

**Files to enhance**:
```
src/crypto_trader/backtesting/
├── engine.py           # Core engine (review)
├── costs.py            # Transaction cost models
├── logger.py           # Detailed trade logging
└── portfolio_engine.py # Multi-strategy backtesting
```

**Success metric**: Backtest produces detailed logs, realistic P&L

---

## Week 2: Web UI Foundation ⭐ CRITICAL

### 2.1 Backend API (FastAPI)
**Priority**: HIGH - Foundation for web UI

**Tasks**:
- [ ] Set up FastAPI application
  - Project structure
  - CORS for frontend
  - API documentation (auto-generated)
- [ ] Core endpoints:
  ```
  GET  /api/strategies              # List all strategies
  GET  /api/strategies/{name}       # Strategy details
  POST /api/backtest                # Run backtest
  GET  /api/backtest/{id}/status    # Check backtest status
  GET  /api/backtest/{id}/results   # Get results
  GET  /api/data/symbols            # Available trading pairs
  GET  /api/data/timeframes         # Available timeframes
  ```
- [ ] Background job queue
  - Backtests run async (can take minutes)
  - Redis or simple in-memory queue
  - Progress tracking
- [ ] WebSocket for real-time updates
  - Backtest progress
  - Live strategy signals (future)

**Files to create**:
```
src/crypto_trader/api/
├── __init__.py
├── main.py             # FastAPI app
├── routes/
│   ├── strategies.py   # Strategy endpoints
│   ├── backtest.py     # Backtest endpoints
│   └── data.py         # Data endpoints
├── models.py           # Pydantic request/response models
├── dependencies.py     # Shared dependencies
└── background.py       # Background job queue
```

**Success metric**: API responds, can trigger backtest via HTTP

---

### 2.2 Frontend Foundation (Streamlit or React)
**Priority**: HIGH - User-facing interface

**Decision point**:
- **Streamlit**: Faster to build, Python-based, good for dashboards
- **React + Plotly**: More professional, better UX, more work

**Recommendation**: Start with Streamlit, can migrate later

**Tasks** (Streamlit path):
- [ ] Set up Streamlit app
- [ ] Page 1: Strategy Browser
  - List all strategies
  - Filter by type/tags
  - Show description, parameters
- [ ] Page 2: Backtest Runner
  - Select strategy
  - Choose symbol, timeframe, date range
  - Configure parameters
  - Run button → shows progress
- [ ] Page 3: Results Viewer
  - Equity curve (interactive)
  - Metrics table (Sharpe, drawdown, etc.)
  - Trade list
  - Parameter sensitivity
- [ ] Page 4: Strategy Comparison
  - Multi-select strategies
  - Side-by-side comparison
  - Heatmap of performance across timeframes

**Files to create**:
```
src/crypto_trader/web/
├── __init__.py
├── app.py              # Main Streamlit app
├── pages/
│   ├── 1_strategies.py
│   ├── 2_backtest.py
│   ├── 3_results.py
│   └── 4_comparison.py
├── components/
│   ├── charts.py       # Reusable chart components
│   ├── tables.py       # Metric tables
│   └── forms.py        # Input forms
└── utils.py            # Helper functions
```

**Success metric**: Can browse strategies, run backtest, see results in browser

---

## Phase 1 Deliverables (End of Week 2)

### Must Have ✅
- [ ] Data quality validation working
- [ ] All existing strategies testable
- [ ] Web UI running (Streamlit)
- [ ] Can run backtest from browser
- [ ] Results display with charts
- [ ] Strategy comparison view

### Nice to Have 🎯
- [ ] Multi-exchange data support
- [ ] Parameter optimization UI
- [ ] Export results to CSV/JSON
- [ ] Save/load backtest configurations

### Future Phases 🚀
- [ ] Live paper trading mode
- [ ] Strategy portfolio allocation
- [ ] Real-time signal monitoring
- [ ] Alert system
- [ ] User authentication
- [ ] Saved workspaces

---

## Technical Decisions

### Web Framework
**Choice**: FastAPI (backend) + Streamlit (frontend)
**Why**:
- FastAPI: Modern, async, auto-docs, easy WebSocket
- Streamlit: Rapid prototyping, Python-only, built for data apps
- Can migrate to React later if needed

### Database
**Choice**: SQLite for now (results storage)
**Why**:
- No external dependencies
- Good enough for local/single-user
- Easy migration to PostgreSQL later

### Task Queue
**Choice**: In-memory queue (simple) → Redis (later)
**Why**:
- Don't need distributed queue yet
- Can run in single process
- Easy upgrade path

### Caching
**Choice**: File-based for market data
**Why**:
- Already implemented
- Works well for historical data
- No Redis dependency initially

---

## Directory Structure (After Phase 1)

```
crypto-trading-clean/
├── src/crypto_trader/
│   ├── data/
│   │   ├── fetchers.py         # Exchange connectors
│   │   ├── validators.py       # NEW: Data quality
│   │   ├── cache_manager.py    # NEW: Better caching
│   │   └── quality_metrics.py  # NEW: Data health
│   ├── strategies/
│   │   ├── library/            # 20+ strategies (keep all!)
│   │   ├── metadata.py         # NEW: Strategy info
│   │   ├── testing.py          # NEW: Test framework
│   │   └── comparison.py       # NEW: Compare strategies
│   ├── backtesting/
│   │   ├── engine.py
│   │   ├── costs.py            # NEW: Better cost modeling
│   │   └── logger.py           # NEW: Detailed logging
│   ├── api/                    # NEW: FastAPI backend
│   │   ├── main.py
│   │   ├── routes/
│   │   └── models.py
│   └── web/                    # NEW: Streamlit UI
│       ├── app.py
│       ├── pages/
│       └── components/
├── tests/                      # NEW: Test suite
│   ├── test_data/
│   ├── test_strategies/
│   └── test_backtesting/
├── docs/                       # NEW: Documentation
├── config/
│   └── default.yaml
└── scripts/
    └── run_web.sh              # NEW: Start web server
```

---

## Success Criteria

**Phase 1 is complete when**:
1. ✅ Web UI loads in browser
2. ✅ Can see list of all strategies
3. ✅ Can configure and run a backtest
4. ✅ Results display with charts and metrics
5. ✅ Can compare 2+ strategies side-by-side
6. ✅ Data quality is validated
7. ✅ Basic tests pass

**Demo scenario**:
```
1. Open browser → http://localhost:8501
2. Navigate to "Strategy Browser"
3. See 20+ strategies with descriptions
4. Click "Backtest" on SMA Crossover
5. Select BTC/USDT, 1h, last 90 days
6. Click "Run Backtest"
7. See progress bar
8. View results: equity curve, metrics, trades
9. Compare with RSI Mean Reversion
10. See side-by-side performance
```

---

## Getting Started - Right Now

### Step 1: Audit Current Code (1 hour)
```bash
cd /home/david/crypto-analysis-fork

# Check data layer
cat src/crypto_trader/data/fetchers.py | head -50

# Check strategy base
cat src/crypto_trader/strategies/base.py | head -100

# Check backtesting engine
cat src/crypto_trader/backtesting/engine.py | head -100

# List all strategies
ls src/crypto_trader/strategies/library/
```

### Step 2: Set Up Development Environment (30 min)
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install web dependencies
pip install fastapi uvicorn streamlit plotly redis
```

### Step 3: Create API Skeleton (1 hour)
Create `src/crypto_trader/api/main.py` with basic FastAPI app

### Step 4: Create Web UI Skeleton (1 hour)
Create `src/crypto_trader/web/app.py` with basic Streamlit pages

### Step 5: First Integration Test (30 min)
Run backtest programmatically, verify it works

---

## Let's Start!

Which would you like to tackle first?

**A) Data Quality Layer** - Make sure we have good data
**B) API Backend** - Set up FastAPI endpoints
**C) Web UI** - Build Streamlit dashboard
**D) Audit existing code** - Understand what we have

I recommend: **D → A → B → C** (audit first, then build foundation)

But you choose - what excites you most?
