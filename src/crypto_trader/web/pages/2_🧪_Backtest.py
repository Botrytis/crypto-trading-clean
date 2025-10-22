"""
Backtest Runner Page

Configure and execute strategy backtests with real-time progress tracking.
"""

import streamlit as st
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Any
from crypto_trader.web.config import API_URL

st.set_page_config(page_title="Backtest", page_icon="🧪", layout="wide")

# API URL
# API_URL now imported from config

# Page header
st.title("🧪 Backtest Runner")
st.markdown("Configure and run strategy backtests on historical data")
st.markdown("---")

# Helper functions
@st.cache_data(ttl=60)
def fetch_strategies():
    """Fetch available strategies."""
    try:
        response = requests.get(f"{API_URL}/api/strategies")
        if response.status_code == 200:
            return response.json().get("strategies", [])
    except:
        pass
    return []

@st.cache_data(ttl=60)
def fetch_symbols():
    """Fetch available trading symbols."""
    try:
        response = requests.get(f"{API_URL}/api/data/symbols")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

@st.cache_data(ttl=60)
def fetch_timeframes():
    """Fetch available timeframes."""
    try:
        response = requests.get(f"{API_URL}/api/data/timeframes")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def run_backtest(config: Dict[str, Any]) -> str:
    """Submit backtest job."""
    try:
        response = requests.post(f"{API_URL}/api/backtest/run", json=config)
        if response.status_code == 200:
            return response.json()["job_id"]
        else:
            st.error(f"Failed to start backtest: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def check_backtest_status(job_id: str) -> Dict[str, Any]:
    """Check backtest job status."""
    try:
        response = requests.get(f"{API_URL}/api/backtest/{job_id}/status")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_backtest_results(job_id: str) -> Dict[str, Any]:
    """Get backtest results."""
    try:
        response = requests.get(f"{API_URL}/api/backtest/{job_id}/results")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Configuration Section
st.markdown("## ⚙️ Configuration")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Strategy Selection")

    # Load strategies
    strategies = fetch_strategies()
    if not strategies:
        st.error("Failed to load strategies. Check API connection.")
        st.stop()

    strategy_names = [s["name"] for s in strategies]
    selected_strategy = st.selectbox(
        "Select Strategy",
        strategy_names,
        help="Choose a trading strategy to backtest"
    )

    # Show strategy info
    strategy_info = next((s for s in strategies if s["name"] == selected_strategy), None)
    if strategy_info:
        with st.expander("📋 Strategy Details"):
            st.markdown(f"**Complexity**: {strategy_info.get('complexity', 'N/A')}")
            st.markdown(f"**Recommended Timeframes**: {', '.join(strategy_info.get('recommended_timeframes', []))}")
            st.markdown(f"**Description**: {strategy_info.get('description', 'N/A')[:200]}")

    st.markdown("### Market Data")

    # Symbol selection
    symbols = fetch_symbols()
    symbol_options = [s["symbol"] for s in symbols] if symbols else ["BTC/USDT", "ETH/USDT"]
    selected_symbol = st.selectbox(
        "Trading Pair",
        symbol_options,
        help="Select cryptocurrency trading pair"
    )

    # Timeframe selection
    timeframes = fetch_timeframes()
    timeframe_options = [tf["value"] for tf in timeframes] if timeframes else ["1h", "4h", "1d"]
    selected_timeframe = st.selectbox(
        "Timeframe",
        timeframe_options,
        index=timeframe_options.index("1h") if "1h" in timeframe_options else 0,
        help="Candlestick timeframe"
    )

with col2:
    st.markdown("### Backtest Parameters")

    # Days of data
    days = st.slider(
        "Historical Data (days)",
        min_value=7,
        max_value=730,
        value=90,
        help="Number of days of historical data to use"
    )

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    st.info(f"📅 Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    # Capital and fees
    initial_capital = st.number_input(
        "Initial Capital (USDT)",
        min_value=100.0,
        max_value=1000000.0,
        value=10000.0,
        step=1000.0,
        help="Starting capital in USDT"
    )

    commission = st.number_input(
        "Commission Rate (%)",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.01,
        help="Trading fee percentage (default 0.1% for Binance)"
    ) / 100

    st.markdown("### Strategy Parameters")

    # Get strategy parameters
    if strategy_info and strategy_info.get('parameters'):
        st.info("Strategy has configurable parameters. Using defaults for now.")
        # TODO: Dynamic parameter inputs based on strategy schema
        strategy_params = strategy_info.get('parameters', {})
    else:
        strategy_params = {}

st.markdown("---")

# Run button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run_button = st.button("🚀 Run Backtest", use_container_width=True, type="primary")

# Execute backtest
if run_button:
    # Build config
    config = {
        "strategy_name": selected_strategy,
        "symbol": selected_symbol,
        "timeframe": selected_timeframe,
        "days": days,
        "initial_capital": initial_capital,
        "commission": commission,
        "parameters": strategy_params
    }

    # Submit job
    with st.spinner("Submitting backtest job..."):
        job_id = run_backtest(config)

    if job_id:
        st.session_state.current_job_id = job_id
        st.success(f"✅ Backtest job submitted! Job ID: `{job_id}`")
        time.sleep(0.5)
        st.rerun()

# Progress tracking
if hasattr(st.session_state, 'current_job_id'):
    job_id = st.session_state.current_job_id

    st.markdown("---")
    st.markdown("## 📊 Backtest Progress")

    # Progress placeholder
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    result_placeholder = st.empty()

    # Poll for status
    max_iterations = 60  # 60 seconds timeout
    iteration = 0

    while iteration < max_iterations:
        status = check_backtest_status(job_id)

        if not status:
            status_placeholder.error("❌ Failed to check status")
            break

        # Update progress
        progress = status.get("progress", 0.0)
        progress_placeholder.progress(progress, text=f"Progress: {int(progress * 100)}%")

        # Update status message
        message = status.get("message", "Processing...")
        current_status = status.get("status", "unknown")

        if current_status == "pending":
            status_placeholder.info(f"⏳ {message}")
        elif current_status == "running":
            status_placeholder.info(f"⚙️ {message}")
        elif current_status == "completed":
            status_placeholder.success(f"✅ {message}")

            # Fetch and display results
            results = get_backtest_results(job_id)
            if results:
                with result_placeholder.container():
                    st.markdown("### 🎉 Backtest Complete!")

                    # Metrics
                    metrics = results.get("metrics", {})
                    cols = st.columns(5)

                    with cols[0]:
                        total_return = metrics.get('total_return') or 0
                        st.metric("Total Return", f"{total_return:.2%}")
                    with cols[1]:
                        sharpe = metrics.get('sharpe_ratio') or 0
                        st.metric("Sharpe Ratio", f"{sharpe:.2f}")
                    with cols[2]:
                        drawdown = metrics.get('max_drawdown') or 0
                        st.metric("Max Drawdown", f"{drawdown:.2%}")
                    with cols[3]:
                        win_rate = metrics.get('win_rate') or 0
                        st.metric("Win Rate", f"{win_rate:.2%}")
                    with cols[4]:
                        st.metric("Total Trades", metrics.get('total_trades') or 0)

                    st.markdown("---")

                    # View full results button
                    if st.button("📊 View Detailed Results", use_container_width=True):
                        st.session_state.result_job_id = job_id
                        st.switch_page("pages/3_📊_Results.py")

            break
        elif current_status == "failed":
            status_placeholder.error(f"❌ {message}")
            break

        time.sleep(1)
        iteration += 1

    if iteration >= max_iterations:
        status_placeholder.warning("⏱️ Status check timed out. Check Results page for completion.")

# Recent jobs
st.markdown("---")
st.markdown("## 📜 Recent Backtests")

try:
    response = requests.get(f"{API_URL}/api/backtest/jobs?limit=5")
    if response.status_code == 200:
        recent_jobs = response.json()

        if recent_jobs:
            for job in recent_jobs:
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

                with col1:
                    job_id_short = job["job_id"][:8]
                    st.markdown(f"**Job**: `{job_id_short}...`")

                with col2:
                    started = job.get("started_at", "N/A")
                    if started != "N/A":
                        started = datetime.fromisoformat(started.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M")
                    st.markdown(f"Started: {started}")

                with col3:
                    status_emoji = {
                        "pending": "⏳",
                        "running": "⚙️",
                        "completed": "✅",
                        "failed": "❌"
                    }
                    status = job.get("status", "unknown")
                    st.markdown(f"{status_emoji.get(status, '❓')} {status}")

                with col4:
                    if status == "completed":
                        if st.button("View", key=f"view_{job['job_id']}"):
                            st.session_state.result_job_id = job["job_id"]
                            st.switch_page("pages/3_📊_Results.py")

                st.markdown("---")
        else:
            st.info("No recent backtests")
except:
    st.warning("Could not load recent jobs")

# Sidebar info
st.sidebar.markdown("### 💡 Tips")
st.sidebar.markdown("""
- Start with shorter periods (30-90 days) for faster results
- Higher timeframes (4h, 1d) are more reliable
- Commission rate affects profitability significantly
- Compare multiple strategies to find best fit
""")

st.sidebar.markdown("### ⚠️ Important")
st.sidebar.markdown("""
- Past performance ≠ future results
- Always paper trade first
- Consider transaction costs
- Test multiple market conditions
""")
