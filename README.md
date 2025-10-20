# Crypto Trading Platform - Strategy Research & Backtesting

**Professional-grade cryptocurrency strategy research platform with web interface.**

**Original**: https://github.com/dedigadot/Crypto-Multi-Pair
**This Fork**: Production-focused with 25+ strategies and full web UI

## ✨ Features

- 📊 **25+ Trading Strategies** - From simple moving averages to advanced machine learning
- 🧪 **Powerful Backtesting** - VectorBT-powered vectorized backtesting engine
- 🌐 **Web Interface** - Beautiful Streamlit UI for strategy exploration
- 📈 **Interactive Charts** - Plotly visualizations for equity curves and performance
- 🔍 **Strategy Comparison** - Side-by-side analysis with heatmaps and radar charts
- ⚡ **Fast API** - RESTful backend with async job processing
- 📦 **Professional Stack** - FastAPI, Streamlit, VectorBT, CCXT

## 🚀 Quick Start

### One-Command Setup

**Linux/macOS:**
```bash
git clone https://github.com/Botrytis/crypto-trading-clean.git
cd crypto-trading-clean
./setup.sh
```

**Windows:**
```bash
git clone https://github.com/Botrytis/crypto-trading-clean.git
cd crypto-trading-clean
setup.bat
```

### Running the Platform

You need **two terminals**:

**Terminal 1 - API Server:**
```bash
source venv/bin/activate     # Linux/macOS
# OR
venv\Scripts\activate.bat    # Windows

./scripts/start_api.sh       # Linux/macOS
# OR
scripts\start_api.bat        # Windows
```

**Terminal 2 - Web UI:**
```bash
source venv/bin/activate     # Linux/macOS
# OR
venv\Scripts\activate.bat    # Windows

./scripts/start_web.sh       # Linux/macOS
# OR
scripts\start_web.bat        # Windows
```

**Open your browser:** http://localhost:8501

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[PHASE1_COMPLETE.md](PHASE1_COMPLETE.md)** - Full feature documentation
- **[AUDIT_REPORT.md](AUDIT_REPORT.md)** - Codebase analysis
- **API Docs** - http://localhost:8001/api/docs (when running)

## 🎯 What You Can Do

### Browse Strategies
- Explore all 25+ strategies with descriptions
- Filter by complexity, category, timeframe
- View parameters and recommended settings

### Run Backtests
- Configure symbol, timeframe, period
- Set initial capital and commission
- Real-time progress tracking
- Instant results preview

### Analyze Results
- Interactive equity curves
- Performance metrics with grades
- Trade-by-trade analysis
- Downloadable reports

### Compare Strategies
- Side-by-side performance comparison
- Multi-dimensional radar charts
- Performance heatmaps
- Conservative vs Aggressive recommendations

## 📊 Sample Strategies

**Trend Following:**
- MACD Cross
- Moving Average Crossover
- ADX Trend
- Supertrend
- Parabolic SAR

**Mean Reversion:**
- RSI Reversal
- Bollinger Bounce
- Stochastic Oscillator

**Volatility:**
- ATR Breakout
- Bollinger Breakout
- Keltner Channel

**Machine Learning:**
- Random Forest Classifier
- XGBoost Momentum
- LSTM Price Prediction

...and many more! See the Strategy Browser in the UI.

## 🏗️ Architecture

```
crypto-trading-clean/
├── src/crypto_trader/
│   ├── api/                 # FastAPI backend
│   │   ├── main.py         # App entry point
│   │   └── routes/         # API endpoints
│   ├── web/                # Streamlit UI
│   │   ├── app.py          # Home page
│   │   └── pages/          # UI pages
│   ├── strategies/         # 25+ strategies
│   ├── backtesting/        # VectorBT engine
│   ├── data/               # Data fetchers
│   ├── risk/               # Risk management
│   └── analysis/           # Performance metrics
├── scripts/                # Startup scripts
│   ├── start_api.sh
│   └── start_web.sh
├── setup.sh                # One-command setup
└── requirements.txt        # Dependencies
```

## 🔧 Technical Stack

**Backend:**
- FastAPI - Modern async web framework
- Uvicorn - ASGI server
- Pydantic - Data validation
- Background tasks - Async job queue

**Frontend:**
- Streamlit - Web framework
- Plotly - Interactive charts
- Pandas - Data manipulation

**Core:**
- VectorBT - Backtesting engine
- CCXT - Exchange connectivity
- Pandas-TA - Technical indicators
- NumPy - Numerical computing

## 📈 Performance

- **API Response Times**: <50ms for most endpoints
- **Backtest Execution**: 5-45s depending on period
- **Concurrent Backtests**: Up to 4 workers
- **Strategy Loading**: <1s for all 25+ strategies

## 🎨 Screenshots

### Home Dashboard
Clean overview with system status and quick links

### Strategy Browser
Browse all strategies with filtering and search

### Backtest Runner
Configure and run backtests with real-time progress

### Results Viewer
Interactive charts, metrics, and trade analysis

### Strategy Comparison
Side-by-side analysis with heatmaps

## 🚧 Current Status

**Phase 1: Complete ✅**
- ✅ FastAPI backend with REST API
- ✅ Streamlit web UI (4 pages)
- ✅ 25+ strategies loaded
- ✅ Backtest execution with progress tracking
- ✅ Results viewer with charts
- ✅ Strategy comparison

**Phase 2: Planned**
- Database integration (PostgreSQL)
- Data quality validation layer
- Export functionality (CSV/JSON)
- User authentication
- Saved configurations

## 🤝 Contributing

PRs welcome! Requirements:
- Tests included
- Documented (code comments + docstrings)
- Linted (ruff)
- Formatted (black)

## 📝 License

MIT (same as original)

## 🙏 Credits

**Original Codebase**: [Crypto-Multi-Pair](https://github.com/dedigadot/Crypto-Multi-Pair) by Dedi Gadot
**Fork**: [crypto-trading-clean](https://github.com/Botrytis/crypto-trading-clean)
**Phase 1 Development**: October 2025

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Botrytis/crypto-trading-clean/issues)
- **Documentation**: See docs in this repo
- **API Docs**: http://localhost:8001/api/docs

---

**Built for people who actually trade, not just backtest.** 🚀
