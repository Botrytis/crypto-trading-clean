"""
Automated Strategy Benchmark Page

Run comprehensive benchmarks comparing all strategies across multiple timeframes,
periods, and symbols with automated analysis and visualizations.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
from datetime import datetime
from crypto_trader.web.config import API_URL

st.set_page_config(page_title="Benchmark", page_icon="🏆", layout="wide")

# Page header
st.title("🏆 Automated Strategy Benchmark")
st.markdown("Compare all strategies across multiple market conditions automatically")
st.markdown("---")

# Helper functions
def run_benchmark(config):
    """Start a benchmark run."""
    try:
        response = requests.post(f"{API_URL}/api/benchmark/run", json=config, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API returned status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error starting benchmark: {str(e)}")
        return None

def get_benchmark_status(job_id):
    """Get benchmark status."""
    try:
        response = requests.get(f"{API_URL}/api/benchmark/{job_id}/status", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_benchmark_results(job_id):
    """Get benchmark results."""
    try:
        response = requests.get(f"{API_URL}/api/benchmark/{job_id}/results", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def list_benchmark_jobs():
    """List recent benchmark jobs."""
    try:
        response = requests.get(f"{API_URL}/api/benchmark/jobs", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

# Configuration Section
st.markdown("## ⚙️ Benchmark Configuration")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Market Conditions")

    symbols = st.multiselect(
        "Trading Pairs",
        ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT"],
        default=["BTC/USDT", "ETH/USDT"],
        help="Test strategies on these symbols"
    )

    timeframes = st.multiselect(
        "Timeframes",
        ["15m", "1h", "4h", "1d"],
        default=["1h", "4h", "1d"],
        help="Test strategies on these timeframes"
    )

    periods = st.multiselect(
        "Historical Periods (days)",
        [7, 14, 30, 60, 90, 180, 365],
        default=[30, 90, 180],
        help="Test strategies over these historical periods"
    )

with col2:
    st.markdown("### Test Parameters")

    initial_capital = st.number_input(
        "Initial Capital (USDT)",
        min_value=1000.0,
        max_value=1000000.0,
        value=10000.0,
        step=1000.0
    )

    commission = st.number_input(
        "Commission Rate (%)",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.01
    ) / 100

    # Estimate total tests
    if symbols and timeframes and periods:
        # Assume 18 strategies
        total_tests = 18 * len(symbols) * len(timeframes) * len(periods)
        estimated_time = total_tests * 0.2 / 60  # ~0.2s per test
        st.info(f"📊 **{total_tests} total tests** ({18} strategies × {len(symbols)} symbols × {len(timeframes)} timeframes × {len(periods)} periods)")
        st.caption(f"Estimated time: ~{estimated_time:.1f} minutes")

# Run button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run_button = st.button("🚀 Run Automated Benchmark", use_container_width=True, type="primary")

if run_button:
    if not symbols or not timeframes or not periods:
        st.error("Please select at least one symbol, timeframe, and period")
    else:
        config = {
            "symbols": symbols,
            "timeframes": timeframes,
            "periods": periods,
            "initial_capital": initial_capital,
            "commission": commission
        }

        with st.spinner("Starting benchmark..."):
            result = run_benchmark(config)

        if result:
            st.session_state.benchmark_job_id = result["job_id"]
            st.success(f"✅ Benchmark started! Job ID: `{result['job_id'][:16]}...`")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Failed to start benchmark")

# Progress tracking
if hasattr(st.session_state, 'benchmark_job_id'):
    job_id = st.session_state.benchmark_job_id

    st.markdown("---")
    st.markdown("## 📊 Benchmark Progress")

    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    result_placeholder = st.empty()

    # Poll for status
    max_iterations = 300  # 5 minutes timeout
    iteration = 0

    while iteration < max_iterations:
        status = get_benchmark_status(job_id)

        if not status:
            status_placeholder.error("❌ Failed to check status")
            break

        # Update progress
        progress = status.get("progress", 0.0)
        progress_placeholder.progress(progress, text=f"Progress: {int(progress * 100)}%")

        # Update status message
        message = status.get("message", "Processing...")
        current_status = status.get("status", "unknown")
        completed = status.get("completed_tests", 0)
        total = status.get("total_tests", 0)
        failed = status.get("failed_tests", 0)

        if current_status == "pending":
            status_placeholder.info(f"⏳ {message}")
        elif current_status == "running":
            status_placeholder.info(f"⚙️ {message} | Completed: {completed}/{total} | Failed: {failed}")
        elif current_status == "completed":
            status_placeholder.success(f"✅ {message}")

            # Fetch and display results
            with st.spinner("Loading results..."):
                results = get_benchmark_results(job_id)

            if results:
                st.session_state.benchmark_results = results
                st.rerun()
            break
        elif current_status == "failed":
            status_placeholder.error(f"❌ {message}")
            break

        time.sleep(1)
        iteration += 1

    if iteration >= max_iterations:
        status_placeholder.warning("⏱️ Status check timed out")

# Display results
if hasattr(st.session_state, 'benchmark_results'):
    results = st.session_state.benchmark_results

    st.markdown("---")
    st.markdown("## 📈 Benchmark Results")

    # Summary metrics
    summary = results.get("summary", {})
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Tests",
            summary.get("total_tests", 0)
        )

    with col2:
        prof_rate = summary.get("profitability_rate", 0)
        st.metric(
            "Profitability Rate",
            f"{prof_rate:.1%}",
            delta=f"{summary.get('profitable_tests', 0)} profitable"
        )

    with col3:
        st.metric(
            "Avg Return",
            f"{summary.get('avg_return', 0):.2%}"
        )

    with col4:
        st.metric(
            "Avg Sharpe",
            f"{summary.get('avg_sharpe', 0):.2f}"
        )

    with col5:
        st.metric(
            "Avg Drawdown",
            f"{summary.get('avg_drawdown', 0):.2%}",
            delta_color="inverse"
        )

    st.markdown("---")

    # Rankings
    rankings = results.get("rankings", {})

    st.markdown("### 🏆 Strategy Rankings")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 By Return",
        "📈 By Sharpe",
        "🛡️ By Drawdown",
        "🎯 By Win Rate",
        "✅ By Consistency"
    ])

    with tab1:
        by_return = rankings.get("by_return", [])
        if by_return:
            df = pd.DataFrame(by_return[:10])
            df["avg_return"] = df["avg_return"].apply(lambda x: f"{x:.2%}")
            df["avg_sharpe"] = df["avg_sharpe"].apply(lambda x: f"{x:.2f}")
            df["profitability_rate"] = df["profitability_rate"].apply(lambda x: f"{x:.1%}")
            st.dataframe(df[["strategy", "avg_return", "avg_sharpe", "profitability_rate", "tests"]], use_container_width=True, hide_index=True)

    with tab2:
        by_sharpe = rankings.get("by_sharpe", [])
        if by_sharpe:
            df = pd.DataFrame(by_sharpe[:10])
            df["avg_sharpe"] = df["avg_sharpe"].apply(lambda x: f"{x:.2f}")
            df["avg_return"] = df["avg_return"].apply(lambda x: f"{x:.2%}")
            df["profitability_rate"] = df["profitability_rate"].apply(lambda x: f"{x:.1%}")
            st.dataframe(df[["strategy", "avg_sharpe", "avg_return", "profitability_rate", "tests"]], use_container_width=True, hide_index=True)

    with tab3:
        by_dd = rankings.get("by_drawdown", [])
        if by_dd:
            df = pd.DataFrame(by_dd[:10])
            df["avg_drawdown"] = df["avg_drawdown"].apply(lambda x: f"{x:.2%}")
            df["avg_return"] = df["avg_return"].apply(lambda x: f"{x:.2%}")
            df["profitability_rate"] = df["profitability_rate"].apply(lambda x: f"{x:.1%}")
            st.dataframe(df[["strategy", "avg_drawdown", "avg_return", "profitability_rate", "tests"]], use_container_width=True, hide_index=True)

    with tab4:
        by_wr = rankings.get("by_win_rate", [])
        if by_wr:
            df = pd.DataFrame(by_wr[:10])
            df["avg_win_rate"] = df["avg_win_rate"].apply(lambda x: f"{x:.1%}")
            df["avg_return"] = df["avg_return"].apply(lambda x: f"{x:.2%}")
            df["profitability_rate"] = df["profitability_rate"].apply(lambda x: f"{x:.1%}")
            st.dataframe(df[["strategy", "avg_win_rate", "avg_return", "profitability_rate", "tests"]], use_container_width=True, hide_index=True)

    with tab5:
        by_consistency = rankings.get("by_consistency", [])
        if by_consistency:
            df = pd.DataFrame(by_consistency[:10])
            df["profitability_rate"] = df["profitability_rate"].apply(lambda x: f"{x:.1%}")
            df["avg_return"] = df["avg_return"].apply(lambda x: f"{x:.2%}")
            df["avg_sharpe"] = df["avg_sharpe"].apply(lambda x: f"{x:.2f}")
            st.dataframe(df[["strategy", "profitability_rate", "avg_return", "avg_sharpe", "tests"]], use_container_width=True, hide_index=True)

    st.markdown("---")

    # Visualizations
    st.markdown("### 📊 Performance Visualization")

    # Heatmap of all strategies
    raw_results = results.get("results", [])
    if raw_results:
        # Create pivot table for heatmap
        df_results = pd.DataFrame(raw_results)

        # Return heatmap by strategy and timeframe
        pivot_return = df_results.pivot_table(
            values=df_results["metrics"].apply(lambda x: x["total_return"]),
            index="strategy",
            columns="timeframe",
            aggfunc="mean"
        )

        fig_heatmap = px.imshow(
            pivot_return,
            labels=dict(x="Timeframe", y="Strategy", color="Avg Return"),
            color_continuous_scale="RdYlGn",
            aspect="auto",
            text_auto=".1%"
        )

        fig_heatmap.update_layout(
            title="Strategy Performance by Timeframe (Avg Return)",
            height=600
        )

        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Bar chart of top strategies
        st.markdown("#### Top 10 Strategies by Average Return")

        top_strategies = rankings.get("by_return", [])[:10]
        if top_strategies:
            df_top = pd.DataFrame(top_strategies)

            fig_bar = px.bar(
                df_top,
                x="strategy",
                y="avg_return",
                color="avg_sharpe",
                title="Top 10 Strategies",
                color_continuous_scale="Viridis",
                text_auto=".2%"
            )

            fig_bar.update_layout(
                xaxis_tickangle=-45,
                height=500
            )

            st.plotly_chart(fig_bar, use_container_width=True)

        # Scatter plot: Return vs Risk
        st.markdown("#### Return vs Risk Analysis")

        strategy_stats = rankings.get("by_return", [])
        if strategy_stats:
            df_scatter = pd.DataFrame(strategy_stats)

            fig_scatter = px.scatter(
                df_scatter,
                x="avg_drawdown",
                y="avg_return",
                size="profitability_rate",
                color="avg_sharpe",
                hover_name="strategy",
                title="Risk-Return Profile",
                labels={
                    "avg_drawdown": "Avg Max Drawdown",
                    "avg_return": "Avg Return",
                    "avg_sharpe": "Avg Sharpe"
                },
                color_continuous_scale="Spectral"
            )

            fig_scatter.update_layout(height=500)
            st.plotly_chart(fig_scatter, use_container_width=True)

    # Actions
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Run New Benchmark", use_container_width=True):
            if hasattr(st.session_state, 'benchmark_job_id'):
                del st.session_state.benchmark_job_id
            if hasattr(st.session_state, 'benchmark_results'):
                del st.session_state.benchmark_results
            st.rerun()

    with col2:
        if st.button("📚 Browse Strategies", use_container_width=True):
            st.switch_page("pages/1_📚_Strategies.py")

    with col3:
        if st.button("🧪 Single Backtest", use_container_width=True):
            st.switch_page("pages/2_🧪_Backtest.py")

# Recent benchmark jobs
if not hasattr(st.session_state, 'benchmark_results'):
    st.markdown("---")
    st.markdown("### 📜 Recent Benchmarks")

    jobs = list_benchmark_jobs()
    if jobs:
        for job in jobs[:5]:
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
                        st.session_state.benchmark_job_id = job["job_id"]
                        results = get_benchmark_results(job["job_id"])
                        if results:
                            st.session_state.benchmark_results = results
                        st.rerun()

            st.markdown("---")
    else:
        st.info("No recent benchmarks")

# Sidebar
st.sidebar.markdown("### 🏆 Benchmark Info")
st.sidebar.markdown("""
**What it does:**
- Tests ALL strategies automatically
- Runs across multiple symbols, timeframes, and periods
- Generates comprehensive comparison reports
- Identifies best performers for different market conditions

**Use cases:**
- Strategy discovery and selection
- Performance validation across markets
- Robustness testing
- Parameter sensitivity analysis
""")

st.sidebar.markdown("### 💡 Tips")
st.sidebar.markdown("""
- Start with 2-3 symbols and timeframes
- Use 30, 90, 180 day periods for broad coverage
- Compare rankings across different metrics
- Look for strategies that rank high across multiple metrics
""")
