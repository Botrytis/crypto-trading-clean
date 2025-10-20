# Quick Start Guide

Get the Crypto Trading Platform running in 5 minutes.

## Prerequisites

- **Python 3.12+** installed
- **Git** installed
- **~500MB** disk space for dependencies

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Botrytis/crypto-trading-clean.git
cd crypto-trading-clean
```

### 2. Run Setup Script

```bash
./setup.sh
```

This will:
- ✅ Create a Python virtual environment (`venv/`)
- ✅ Install all dependencies (~85 packages)
- ✅ Install the `crypto-trader` package in development mode
- ✅ Verify the installation

**Note**: Setup takes 5-10 minutes depending on your internet connection.

### 3. Start the Platform

You need **two terminals**:

**Terminal 1 - API Server:**
```bash
cd crypto-trading-clean
source venv/bin/activate  # Activate virtual environment
./scripts/start_api.sh
```

Wait for: `✅ API ready!`

**Terminal 2 - Web UI:**
```bash
cd crypto-trading-clean
source venv/bin/activate  # Activate virtual environment
./scripts/start_web.sh
```

Wait for: `You can now view your Streamlit app in your browser.`

### 4. Open Your Browser

Navigate to: **http://localhost:8501**

You should see the Crypto Trading Platform home page! 🎉

---

## Quick Test

Once both servers are running:

1. **Browse Strategies**: Click "📚 Strategies" in the sidebar
2. **Run a Backtest**:
   - Click "🧪 Backtest" in the sidebar
   - Select any strategy (e.g., "MACD Cross")
   - Choose BTC/USDT
   - Set 30 days
   - Click "🚀 Run Backtest"
3. **View Results**: Wait ~10 seconds, then click "📊 View Detailed Results"

---

## Troubleshooting

### Port 8001 already in use

```bash
# Kill the process using port 8001
lsof -ti:8001 | xargs kill -9

# Or use a different port
# Edit scripts/start_api.sh and change 8001 to 8002
```

### Port 8501 already in use

```bash
# Kill the process using port 8501
lsof -ti:8501 | xargs kill -9

# Or Streamlit will auto-assign a new port
```

### Module not found errors

```bash
# Reinstall the package
source venv/bin/activate
pip install -e .
```

### Dependencies installation failed

```bash
# Clean install
rm -rf venv
./setup.sh
```

---

## What's Next?

- 📖 **Read the docs**: See `PHASE1_COMPLETE.md` for full feature list
- 🔧 **API Documentation**: http://localhost:8001/api/docs
- 📊 **Explore strategies**: Browse all 25+ strategies
- 🧪 **Run backtests**: Test strategies on historical data
- 🔍 **Compare results**: Find the best performing strategies

---

## Stopping the Servers

**Terminal 1 (API):** Press `CTRL+C`

**Terminal 2 (Web UI):** Press `CTRL+C`

---

## System Requirements

- **Python**: 3.12 or higher
- **RAM**: 2GB minimum (4GB recommended for backtests)
- **Disk**: 500MB for dependencies + data cache
- **OS**: Linux, macOS, or Windows (with WSL)

---

## Need Help?

- **GitHub Issues**: https://github.com/Botrytis/crypto-trading-clean/issues
- **Documentation**: See `README.md` and `PHASE1_COMPLETE.md`
- **API Docs**: http://localhost:8001/api/docs (when server is running)

---

**Ready to explore crypto trading strategies!** 🚀
