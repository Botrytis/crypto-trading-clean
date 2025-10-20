"""
Results Viewer Page

Display detailed backtest results with charts, metrics, and trade analysis.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

st.set_page_config(page_title="Results", page_icon="📊", layout="wide")

# API URL
API_URL = "http://localhost:8001"

# Page header
st.title("📊 Backtest Results")
st.markdown("Detailed analysis of strategy performance")
st.markdown("---")

# Helper functions
def get_backtest_results(job_id: str):
    """Fetch backtest results."""
    try:
        response = requests.get(f"{API_URL}/api/backtest/{job_id}/results")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def create_equity_curve_chart(equity_data):
    """Create interactive equity curve chart."""
    df = pd.DataFrame(equity_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['equity'],
        mode='lines',
        name='Portfolio Value',
        line=dict(color='#1f77b4', width=2),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.1)'
    ))

    fig.update_layout(
        title="Equity Curve",
        xaxis_title="Date",
        yaxis_title="Portfolio Value (USDT)",
        hovermode='x unified',
        template='plotly_white',
        height=500
    )

    return fig

def create_trades_chart(trades_data):
    """Create trades visualization."""
    if not trades_data:
        return None

    df = pd.DataFrame(trades_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Separate winning and losing trades
    wins = df[df['pnl'] > 0]
    losses = df[df['pnl'] <= 0]

    fig = go.Figure()

    # Winning trades
    if len(wins) > 0:
        fig.add_trace(go.Scatter(
            x=wins['timestamp'],
            y=wins['pnl'],
            mode='markers',
            name='Winning Trades',
            marker=dict(color='green', size=8, symbol='triangle-up')
        ))

    # Losing trades
    if len(losses) > 0:
        fig.add_trace(go.Scatter(
            x=losses['timestamp'],
            y=losses['pnl'],
            mode='markers',
            name='Losing Trades',
            marker=dict(color='red', size=8, symbol='triangle-down')
        ))

    fig.update_layout(
        title="Trade P&L Distribution",
        xaxis_title="Date",
        yaxis_title="P&L (USDT)",
        hovermode='closest',
        template='plotly_white',
        height=400
    )

    return fig

# Check if we have a result to display
if not hasattr(st.session_state, 'result_job_id'):
    st.info("ℹ️ No backtest results selected. Run a backtest from the Backtest page.")

    # Show recent jobs
    st.markdown("### Recent Completed Backtests")
    try:
        response = requests.get(f"{API_URL}/api/backtest/jobs?limit=10")
        if response.status_code == 200:
            jobs = response.json()
            completed_jobs = [j for j in jobs if j.get("status") == "completed"]

            if completed_jobs:
                cols = st.columns(3)
                for idx, job in enumerate(completed_jobs[:9]):
                    with cols[idx % 3]:
                        job_id_short = job["job_id"][:8]
                        started = job.get("started_at", "N/A")
                        if started != "N/A":
                            started = datetime.fromisoformat(started.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M")

                        if st.button(f"📊 Job {job_id_short}...\n{started}", key=f"load_{job['job_id']}", use_container_width=True):
                            st.session_state.result_job_id = job["job_id"]
                            st.rerun()
            else:
                st.warning("No completed backtests found")
    except:
        st.error("Failed to load recent jobs")

    st.stop()

# Load results
job_id = st.session_state.result_job_id

with st.spinner("Loading results..."):
    results = get_backtest_results(job_id)

if not results:
    st.error(f"Failed to load results for job {job_id}")
    if st.button("Clear"):
        del st.session_state.result_job_id
        st.rerun()
    st.stop()

# Display results
st.markdown(f"### Strategy: {results['strategy_name']}")
st.markdown(f"**Symbol**: {results['symbol']} | **Timeframe**: {results['timeframe']} | **Job ID**: `{job_id[:16]}...`")

st.markdown("---")

# Key Metrics
st.markdown("## 📈 Performance Metrics")

metrics = results.get("metrics", {})

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_return = metrics.get('total_return', 0)
    delta_color = "normal" if total_return >= 0 else "inverse"
    st.metric(
        "Total Return",
        f"{total_return:.2%}",
        delta=f"{total_return:.2%}",
        delta_color=delta_color
    )

with col2:
    sharpe = metrics.get('sharpe_ratio', 0)
    sharpe_grade = "🟢" if sharpe > 1.5 else "🟡" if sharpe > 1.0 else "🔴"
    st.metric(
        "Sharpe Ratio",
        f"{sharpe:.2f} {sharpe_grade}",
        help="Risk-adjusted return (>1.0 is good, >1.5 is excellent)"
    )

with col3:
    drawdown = metrics.get('max_drawdown', 0)
    dd_grade = "🟢" if abs(drawdown) < 0.2 else "🟡" if abs(drawdown) < 0.3 else "🔴"
    st.metric(
        "Max Drawdown",
        f"{drawdown:.2%} {dd_grade}",
        delta=f"{drawdown:.2%}",
        delta_color="inverse",
        help="Largest peak-to-trough decline (<20% is good)"
    )

with col4:
    win_rate = metrics.get('win_rate', 0)
    wr_grade = "🟢" if win_rate > 0.55 else "🟡" if win_rate > 0.45 else "🔴"
    st.metric(
        "Win Rate",
        f"{win_rate:.2%} {wr_grade}",
        help="Percentage of profitable trades (>50% is good)"
    )

with col5:
    total_trades = metrics.get('total_trades', 0)
    st.metric(
        "Total Trades",
        f"{total_trades}",
        help="Number of completed trades"
    )

st.markdown("---")

# Charts
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📈 Equity Curve")
    equity_data = results.get("equity_curve", [])
    if equity_data:
        chart = create_equity_curve_chart(equity_data)
        st.plotly_chart(chart, use_container_width=True)
    else:
        st.warning("No equity curve data available")

with col2:
    st.markdown("### 📊 Trade Statistics")

    trades_data = results.get("trades", [])
    if trades_data:
        df_trades = pd.DataFrame(trades_data)

        # Calculate stats
        winning_trades = len(df_trades[df_trades['pnl'] > 0])
        losing_trades = len(df_trades[df_trades['pnl'] <= 0])
        avg_win = df_trades[df_trades['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = df_trades[df_trades['pnl'] <= 0]['pnl'].mean() if losing_trades > 0 else 0

        st.metric("Winning Trades", f"{winning_trades}")
        st.metric("Losing Trades", f"{losing_trades}")
        st.metric("Avg Win", f"${avg_win:.2f}")
        st.metric("Avg Loss", f"${avg_loss:.2f}")

        if avg_loss != 0:
            profit_factor = abs(avg_win / avg_loss) if avg_loss < 0 else 0
            pf_grade = "🟢" if profit_factor > 2 else "🟡" if profit_factor > 1 else "🔴"
            st.metric("Profit Factor", f"{profit_factor:.2f} {pf_grade}")

    else:
        st.info("No trade data available")

# Trade P&L Chart
st.markdown("### 💹 Trade P&L Over Time")
trades_data = results.get("trades", [])
if trades_data:
    trades_chart = create_trades_chart(trades_data)
    if trades_chart:
        st.plotly_chart(trades_chart, use_container_width=True)
else:
    st.warning("No trade data available")

st.markdown("---")

# Trade List
st.markdown("### 📋 Trade History")
if trades_data:
    df_trades = pd.DataFrame(trades_data)
    df_trades['timestamp'] = pd.to_datetime(df_trades['timestamp'])
    df_trades['timestamp'] = df_trades['timestamp'].dt.strftime('%Y-%m-%d %H:%M')

    # Format for display
    df_display = df_trades.copy()
    df_display['P&L'] = df_display['pnl'].apply(lambda x: f"${x:.2f}")
    df_display['Price'] = df_display['price'].apply(lambda x: f"${x:.2f}")

    # Color code P&L
    def color_pnl(val):
        if 'pnl' in val.name:
            color = 'green' if val > 0 else 'red'
            return [f'color: {color}' for _ in val]
        return ['' for _ in val]

    st.dataframe(
        df_display[['timestamp', 'side', 'Price', 'P&L']].head(100),
        use_container_width=True,
        hide_index=True
    )

    if len(df_trades) > 100:
        st.info(f"Showing first 100 of {len(df_trades)} trades")
else:
    st.info("No trades executed during backtest")

st.markdown("---")

# Export and actions
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Run Another Backtest", use_container_width=True):
        st.switch_page("pages/2_🧪_Backtest.py")

with col2:
    if st.button("📊 Compare Strategies", use_container_width=True):
        st.switch_page("pages/4_🔍_Comparison.py")

with col3:
    if st.button("❌ Clear Results"):
        del st.session_state.result_job_id
        st.rerun()

# Sidebar - interpretation guide
st.sidebar.markdown("### 📖 Metrics Guide")

st.sidebar.markdown("""
**Total Return**
- Overall profit/loss percentage
- 🟢 Positive is profitable
- 🔴 Negative is losing money

**Sharpe Ratio**
- Risk-adjusted returns
- 🟢 >1.5 Excellent
- 🟡 >1.0 Good
- 🔴 <1.0 Poor

**Max Drawdown**
- Largest peak-to-trough decline
- 🟢 <20% Good
- 🟡 <30% Acceptable
- 🔴 >30% High risk

**Win Rate**
- % of profitable trades
- 🟢 >55% Good
- 🟡 >45% Average
- 🔴 <45% Poor

**Profit Factor**
- Avg Win / Avg Loss
- 🟢 >2.0 Excellent
- 🟡 >1.0 Profitable
- 🔴 <1.0 Losing
""")
