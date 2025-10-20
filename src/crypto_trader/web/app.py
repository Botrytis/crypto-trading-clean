"""
Crypto Trading Platform - Streamlit Web UI

Main application entry point for the multi-page Streamlit dashboard.

Run with:
    streamlit run src/crypto_trader/web/app.py
"""

import streamlit as st
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Crypto Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .strategy-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .strategy-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        border-color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=Crypto+Trading", use_container_width=True)
    st.markdown("---")

    st.markdown("### 🎯 Navigation")
    st.markdown("Use the pages above to:")
    st.markdown("- 📚 Browse strategies")
    st.markdown("- 🧪 Run backtests")
    st.markdown("- 📊 View results")
    st.markdown("- 🔍 Compare strategies")

    st.markdown("---")

    st.markdown("### ⚙️ System Status")
    # Check API connectivity
    import requests
    try:
        response = requests.get("http://localhost:8001/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Offline")
        st.caption("Start API: `./scripts/start_api.sh`")

    st.markdown("---")
    st.caption("v0.1.0 | Phase 1")

# Main content
st.markdown('<div class="main-header">📈 Crypto Trading Research Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Strategy Analysis • Backtesting • Portfolio Research</div>', unsafe_allow_html=True)

# Welcome section
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="📚 Available Strategies",
        value="25+",
        delta="All strategies loaded"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="💹 Trading Pairs",
        value="10+",
        delta="Binance USDT pairs"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="⏱️ Timeframes",
        value="8",
        delta="1m to 1w"
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Quick Start Guide
st.markdown("## 🚀 Quick Start Guide")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 1️⃣ Browse Strategies")
    st.markdown("""
    - Navigate to **📚 Strategies** page
    - Explore 25+ trading strategies
    - Filter by type, complexity, or tags
    - View parameters and descriptions
    """)

    st.markdown("### 2️⃣ Run Backtests")
    st.markdown("""
    - Go to **🧪 Backtest** page
    - Select a strategy
    - Configure symbol, timeframe, period
    - Adjust strategy parameters
    - Click **Run Backtest**
    """)

with col2:
    st.markdown("### 3️⃣ Analyze Results")
    st.markdown("""
    - Check **📊 Results** page
    - View equity curves
    - Analyze metrics (Sharpe, drawdown, etc.)
    - Review trade history
    - Export data
    """)

    st.markdown("### 4️⃣ Compare Strategies")
    st.markdown("""
    - Visit **🔍 Comparison** page
    - Select multiple strategies
    - Compare side-by-side
    - Identify best performers
    """)

st.markdown("---")

# Strategy Categories
st.markdown("## 📂 Strategy Categories")

categories = {
    "🎯 Trend Following": [
        "SMA Crossover",
        "Triple EMA",
        "Supertrend ATR",
        "Ichimoku Cloud",
        "Moving Average Crossover"
    ],
    "📉 Mean Reversion": [
        "RSI Mean Reversion",
        "Bollinger Breakout",
        "VWAP Mean Reversion"
    ],
    "💼 Portfolio Management": [
        "Portfolio Rebalancer",
        "Hierarchical Risk Parity",
        "Black-Litterman",
        "Risk Parity"
    ],
    "🤖 Machine Learning": [
        "Deep RL Portfolio",
        "DDQN Feature Selected",
        "Transformer GRU Predictor",
        "Dynamic Ensemble"
    ],
    "🔗 Pairs Trading": [
        "Statistical Arbitrage",
        "Copula Pairs Trading"
    ],
    "📊 Multi-Factor": [
        "Multi-Timeframe Confluence",
        "Regime Adaptive",
        "Multimodal Sentiment Fusion"
    ],
}

cols = st.columns(3)
for idx, (category, strategies) in enumerate(categories.items()):
    with cols[idx % 3]:
        st.markdown(f"### {category}")
        for strategy in strategies:
            st.markdown(f"- {strategy}")

st.markdown("---")

# Footer
st.markdown("### 📖 Documentation")
st.markdown("""
- **API Docs**: [http://localhost:8001/api/docs](http://localhost:8001/api/docs)
- **GitHub**: [crypto-trading-clean](https://github.com/Botrytis/crypto-trading-clean)
- **Phase 1 Plan**: See `PHASE1_REVISED.md` in repo
""")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit, FastAPI, and VectorBT | Phase 1 Development")
