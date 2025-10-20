"""
Strategy Comparison Page

Compare multiple strategies side-by-side with performance heatmaps.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Comparison", page_icon="🔍", layout="wide")

# API URL
API_URL = "http://localhost:8001"

# Page header
st.title("🔍 Strategy Comparison")
st.markdown("Compare multiple strategies to find the best performer")
st.markdown("---")

# Load completed jobs
@st.cache_data(ttl=30)
def load_completed_jobs():
    """Load completed backtest jobs."""
    try:
        response = requests.get(f"{API_URL}/api/backtest/jobs?limit=50")
        if response.status_code == 200:
            all_jobs = response.json()
            completed = [j for j in all_jobs if j.get("status") == "completed"]
            return completed
        return []
    except:
        return []

def get_job_results(job_id):
    """Get results for a specific job."""
    try:
        response = requests.get(f"{API_URL}/api/backtest/{job_id}/results")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Load jobs
jobs = load_completed_jobs()

if not jobs:
    st.warning("No completed backtests available for comparison. Run some backtests first!")
    if st.button("🧪 Go to Backtest Page"):
        st.switch_page("pages/2_🧪_Backtest.py")
    st.stop()

# Job selection
st.markdown("### Select Backtests to Compare")

# Create a nice display of jobs
job_options = []
for job in jobs:
    job_id = job["job_id"]
    started = job.get("started_at", "Unknown")
    if started != "Unknown":
        from datetime import datetime
        started = datetime.fromisoformat(started.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M")

    # Try to get basic info
    results = get_job_results(job_id)
    if results:
        strategy = results.get("strategy_name", "Unknown")
        symbol = results.get("symbol", "N/A")
        timeframe = results.get("timeframe", "N/A")
        label = f"{strategy} | {symbol} | {timeframe} | {started}"
        job_options.append((label, job_id))

if not job_options:
    st.error("Could not load job details")
    st.stop()

# Multi-select
selected_labels = st.multiselect(
    "Select 2-5 backtests to compare",
    [label for label, _ in job_options],
    max_selections=5,
    help="Choose multiple backtests to compare side-by-side"
)

if len(selected_labels) < 2:
    st.info("👆 Please select at least 2 backtests to compare")
    st.stop()

# Get selected job IDs
selected_jobs = [job_id for label, job_id in job_options if label in selected_labels]

# Load results for all selected jobs
st.markdown("---")
st.markdown("### 📊 Comparison Results")

with st.spinner("Loading results..."):
    results_data = []
    for job_id in selected_jobs:
        result = get_job_results(job_id)
        if result:
            results_data.append(result)

if not results_data:
    st.error("Failed to load results")
    st.stop()

# Create comparison dataframe
comparison_data = []
for result in results_data:
    metrics = result.get("metrics", {})
    comparison_data.append({
        "Strategy": result.get("strategy_name", "Unknown"),
        "Symbol": result.get("symbol", "N/A"),
        "Timeframe": result.get("timeframe", "N/A"),
        "Total Return": metrics.get("total_return", 0),
        "Sharpe Ratio": metrics.get("sharpe_ratio", 0),
        "Max Drawdown": metrics.get("max_drawdown", 0),
        "Win Rate": metrics.get("win_rate", 0),
        "Total Trades": metrics.get("total_trades", 0),
    })

df_comparison = pd.DataFrame(comparison_data)

# Summary metrics
st.markdown("#### 📈 Performance Metrics Comparison")

col1, col2 = st.columns(2)

with col1:
    # Format for display
    df_display = df_comparison.copy()
    df_display["Total Return"] = df_display["Total Return"].apply(lambda x: f"{x:.2%}")
    df_display["Sharpe Ratio"] = df_display["Sharpe Ratio"].apply(lambda x: f"{x:.2f}")
    df_display["Max Drawdown"] = df_display["Max Drawdown"].apply(lambda x: f"{x:.2%}")
    df_display["Win Rate"] = df_display["Win Rate"].apply(lambda x: f"{x:.2%}")

    st.dataframe(df_display, use_container_width=True, hide_index=True)

with col2:
    st.markdown("**Best Performers**")

    # Find best in each category
    best_return_idx = df_comparison["Total Return"].idxmax()
    best_sharpe_idx = df_comparison["Sharpe Ratio"].idxmax()
    best_drawdown_idx = df_comparison["Max Drawdown"].idxmax()  # Least negative
    best_wr_idx = df_comparison["Win Rate"].idxmax()

    st.markdown(f"🏆 **Highest Return**: {df_comparison.loc[best_return_idx, 'Strategy']} ({df_comparison.loc[best_return_idx, 'Total Return']:.2%})")
    st.markdown(f"📊 **Best Sharpe**: {df_comparison.loc[best_sharpe_idx, 'Strategy']} ({df_comparison.loc[best_sharpe_idx, 'Sharpe Ratio']:.2f})")
    st.markdown(f"🛡️ **Lowest Drawdown**: {df_comparison.loc[best_drawdown_idx, 'Strategy']} ({df_comparison.loc[best_drawdown_idx, 'Max Drawdown']:.2%})")
    st.markdown(f"🎯 **Best Win Rate**: {df_comparison.loc[best_wr_idx, 'Strategy']} ({df_comparison.loc[best_wr_idx, 'Win Rate']:.2%})")

st.markdown("---")

# Visual comparisons
st.markdown("#### 📊 Visual Comparison")

# Metric selection for charts
metric_to_plot = st.selectbox(
    "Select metric to visualize",
    ["Total Return", "Sharpe Ratio", "Max Drawdown", "Win Rate", "Total Trades"]
)

# Bar chart comparison
fig_bar = px.bar(
    df_comparison,
    x="Strategy",
    y=metric_to_plot,
    color=metric_to_plot,
    title=f"{metric_to_plot} Comparison",
    text_auto='.2f' if metric_to_plot in ["Sharpe Ratio", "Total Trades"] else '.2%',
    color_continuous_scale="RdYlGn" if metric_to_plot != "Max Drawdown" else "RdYlGn_r"
)

fig_bar.update_layout(
    height=400,
    showlegend=False,
    template="plotly_white"
)

st.plotly_chart(fig_bar, use_container_width=True)

# Heatmap of all metrics
st.markdown("#### 🔥 Performance Heatmap")

# Normalize metrics for heatmap (0-1 scale)
df_normalized = df_comparison.copy()
for col in ["Total Return", "Sharpe Ratio", "Win Rate"]:
    if col in df_normalized.columns:
        min_val = df_normalized[col].min()
        max_val = df_normalized[col].max()
        if max_val > min_val:
            df_normalized[col] = (df_normalized[col] - min_val) / (max_val - min_val)
        else:
            df_normalized[col] = 0.5

# Max Drawdown (inverse - lower is better)
if "Max Drawdown" in df_normalized.columns:
    min_val = df_normalized["Max Drawdown"].min()
    max_val = df_normalized["Max Drawdown"].max()
    if max_val > min_val:
        df_normalized["Max Drawdown"] = 1 - (df_normalized["Max Drawdown"] - min_val) / (max_val - min_val)
    else:
        df_normalized["Max Drawdown"] = 0.5

# Create heatmap data
heatmap_data = df_normalized[["Strategy", "Total Return", "Sharpe Ratio", "Max Drawdown", "Win Rate"]].set_index("Strategy").T

fig_heatmap = px.imshow(
    heatmap_data.values,
    labels=dict(x="Strategy", y="Metric", color="Normalized Score"),
    x=heatmap_data.columns,
    y=heatmap_data.index,
    color_continuous_scale="RdYlGn",
    aspect="auto",
    text_auto=".2f"
)

fig_heatmap.update_layout(
    title="Normalized Performance Heatmap (Green=Better, Red=Worse)",
    height=400,
    template="plotly_white"
)

st.plotly_chart(fig_heatmap, use_container_width=True)

# Radar chart
st.markdown("#### 🎯 Multi-Dimensional Comparison")

# Create radar chart
fig_radar = go.Figure()

for _, row in df_normalized.iterrows():
    fig_radar.add_trace(go.Scatterpolar(
        r=[
            row["Total Return"],
            row["Sharpe Ratio"],
            row["Max Drawdown"],
            row["Win Rate"],
            row["Total Return"]  # Close the loop
        ],
        theta=["Return", "Sharpe", "Drawdown", "Win Rate", "Return"],
        fill='toself',
        name=row["Strategy"]
    ))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 1])
    ),
    showlegend=True,
    title="Strategy Performance Radar (Normalized)",
    height=500,
    template="plotly_white"
)

st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")

# Recommendations
st.markdown("### 💡 Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### For Conservative Investors")
    # Find strategy with best Sharpe and lowest drawdown
    df_comparison["Conservative Score"] = (
        df_comparison["Sharpe Ratio"] * 0.5 +
        (1 + df_comparison["Max Drawdown"]) * 0.5  # Less negative drawdown is better
    )
    best_conservative = df_comparison.loc[df_comparison["Conservative Score"].idxmax()]

    st.success(f"**Recommended**: {best_conservative['Strategy']}")
    st.markdown(f"- Sharpe Ratio: {best_conservative['Sharpe Ratio']:.2f}")
    st.markdown(f"- Max Drawdown: {best_conservative['Max Drawdown']:.2%}")
    st.markdown(f"- Total Return: {best_conservative['Total Return']:.2%}")

with col2:
    st.markdown("#### For Aggressive Investors")
    # Find strategy with highest return
    best_aggressive = df_comparison.loc[df_comparison["Total Return"].idxmax()]

    st.success(f"**Recommended**: {best_aggressive['Strategy']}")
    st.markdown(f"- Total Return: {best_aggressive['Total Return']:.2%}")
    st.markdown(f"- Sharpe Ratio: {best_aggressive['Sharpe Ratio']:.2f}")
    st.markdown(f"- Max Drawdown: {best_aggressive['Max Drawdown']:.2%}")

# Actions
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 New Comparison", use_container_width=True):
        st.rerun()

with col2:
    if st.button("🧪 Run More Backtests", use_container_width=True):
        st.switch_page("pages/2_🧪_Backtest.py")

with col3:
    if st.button("📚 Browse Strategies", use_container_width=True):
        st.switch_page("pages/1_📚_Strategies.py")

# Sidebar help
st.sidebar.markdown("### 📊 Comparison Tips")
st.sidebar.markdown("""
- Compare strategies on same symbol/timeframe for fair comparison
- Look for consistent performers across multiple metrics
- High return with high drawdown = risky
- Sharpe ratio shows risk-adjusted performance
- Win rate alone doesn't tell full story
""")

st.sidebar.markdown("### 🎯 Scoring Logic")
st.sidebar.markdown("""
**Conservative Score**
- 50% Sharpe Ratio
- 50% Drawdown Protection

**Aggressive Score**
- 100% Total Return

**Balanced Score** (coming soon)
- 40% Return
- 30% Sharpe
- 20% Drawdown
- 10% Win Rate
""")
