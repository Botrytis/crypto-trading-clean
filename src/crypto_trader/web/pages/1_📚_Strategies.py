"""
from crypto_trader.web.config import API_URL
Strategy Browser Page

Browse, search, and filter all available trading strategies.
"""

import streamlit as st
import requests
import pandas as pd
from typing import List, Dict, Any

st.set_page_config(page_title="Strategies", page_icon="📚", layout="wide")

# API URL
# API_URL now imported from config

# Page header
st.title("📚 Strategy Browser")
st.markdown("Explore **25+ trading strategies** for cryptocurrency markets")
st.markdown("---")

# Helper functions
@st.cache_data(ttl=60)
def fetch_strategies() -> List[Dict[str, Any]]:
    """Fetch strategies from API."""
    try:
        response = requests.get(f"{API_URL}/api/strategies", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("strategies", [])
        else:
            st.error(f"API Error: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Failed to connect to API: {e}")
        st.info("💡 Make sure API is running: `./scripts/start_api.sh`")
        return []


def categorize_strategy(tags: List[str]) -> str:
    """Categorize strategy based on tags."""
    if not tags:
        return "Other"

    # Simple categorization logic
    tag_lower = [t.lower() for t in tags]

    if any(t in tag_lower for t in ["trend", "moving-average", "crossover"]):
        return "Trend Following"
    elif any(t in tag_lower for t in ["mean-reversion", "rsi", "bollinger"]):
        return "Mean Reversion"
    elif any(t in tag_lower for t in ["portfolio", "allocation"]):
        return "Portfolio"
    elif any(t in tag_lower for t in ["ml", "deep-learning", "neural"]):
        return "Machine Learning"
    elif any(t in tag_lower for t in ["pairs", "arbitrage"]):
        return "Pairs Trading"
    else:
        return "Other"


# Load strategies
with st.spinner("Loading strategies..."):
    strategies = fetch_strategies()

if not strategies:
    st.warning("No strategies available. Check API connection.")
    st.stop()

# Filters
st.sidebar.markdown("### 🔍 Filters")

# Search
search_term = st.sidebar.text_input("🔎 Search", placeholder="Strategy name...")

# Complexity filter
complexity_options = ["All"] + sorted(list(set([s.get("complexity", "medium") for s in strategies])))
complexity_filter = st.sidebar.selectbox("📊 Complexity", complexity_options)

# Category filter (derived from tags)
categories = set([categorize_strategy(s.get("tags", [])) for s in strategies])
category_options = ["All"] + sorted(list(categories))
category_filter = st.sidebar.selectbox("📂 Category", category_options)

# Timeframe filter
all_timeframes = set()
for s in strategies:
    all_timeframes.update(s.get("recommended_timeframes", []))
timeframe_options = ["All"] + sorted(list(all_timeframes))
timeframe_filter = st.sidebar.selectbox("⏱️ Timeframe", timeframe_options)

# Apply filters
filtered_strategies = strategies

if search_term:
    filtered_strategies = [
        s for s in filtered_strategies
        if search_term.lower() in s["name"].lower() or
           search_term.lower() in s.get("description", "").lower()
    ]

if complexity_filter != "All":
    filtered_strategies = [
        s for s in filtered_strategies
        if s.get("complexity", "medium") == complexity_filter
    ]

if category_filter != "All":
    filtered_strategies = [
        s for s in filtered_strategies
        if categorize_strategy(s.get("tags", [])) == category_filter
    ]

if timeframe_filter != "All":
    filtered_strategies = [
        s for s in filtered_strategies
        if timeframe_filter in s.get("recommended_timeframes", [])
    ]

# Display results count
st.markdown(f"### Found {len(filtered_strategies)} strategies")
st.markdown("---")

# View mode toggle
view_mode = st.radio("View", ["Cards", "Table"], horizontal=True)

if view_mode == "Cards":
    # Card view
    for strategy in filtered_strategies:
        with st.container():
            # Create card with custom styling
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### {strategy['name']}")
                st.markdown(strategy.get('description', 'No description available')[:200] + "...")

                # Tags
                if strategy.get('tags'):
                    tags_html = " ".join([f'<span style="background-color: #e0e0e0; padding: 0.2rem 0.5rem; border-radius: 0.3rem; margin-right: 0.5rem;">{tag}</span>' for tag in strategy['tags'][:5]])
                    st.markdown(tags_html, unsafe_allow_html=True)

            with col2:
                # Complexity badge
                complexity = strategy.get('complexity', 'medium')
                color_map = {
                    'low': '#4caf50',
                    'medium': '#ff9800',
                    'high': '#f44336'
                }
                color = color_map.get(complexity, '#999')
                st.markdown(f'<div style="background-color: {color}; color: white; padding: 0.5rem; border-radius: 0.3rem; text-align: center; font-weight: bold;">{complexity.upper()}</div>', unsafe_allow_html=True)

                st.markdown("**Timeframes:**")
                timeframes = strategy.get('recommended_timeframes', ['N/A'])
                st.markdown(", ".join(timeframes[:3]))

                # View details button
                if st.button(f"📋 Details", key=f"details_{strategy['name']}"):
                    st.session_state.selected_strategy = strategy['name']
                    st.rerun()

            st.markdown("---")

else:
    # Table view
    df_data = []
    for strategy in filtered_strategies:
        df_data.append({
            "Name": strategy['name'],
            "Category": categorize_strategy(strategy.get('tags', [])),
            "Complexity": strategy.get('complexity', 'medium'),
            "Timeframes": ", ".join(strategy.get('recommended_timeframes', [])[:3]),
            "Parameters": len(strategy.get('parameters', {}))
        })

    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

# Strategy details modal (if selected)
if hasattr(st.session_state, 'selected_strategy'):
    strategy_name = st.session_state.selected_strategy

    # Fetch detailed info
    try:
        response = requests.get(f"{API_URL}/api/strategies/{strategy_name}")
        if response.status_code == 200:
            strategy_detail = response.json()

            st.markdown("---")
            st.markdown(f"## 📋 {strategy_detail['name']} - Details")

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("### Description")
                st.markdown(strategy_detail.get('description', 'No description available'))

                st.markdown("### Parameters")
                params = strategy_detail.get('parameters', {})
                if params:
                    for param_name, param_value in params.items():
                        st.markdown(f"- **{param_name}**: `{param_value}`")
                else:
                    st.info("No configurable parameters")

            with col2:
                st.markdown("### Metadata")
                st.markdown(f"**Complexity**: {strategy_detail.get('complexity', 'N/A')}")
                st.markdown(f"**Tags**: {', '.join(strategy_detail.get('tags', []))}")
                st.markdown(f"**Recommended Timeframes**: {', '.join(strategy_detail.get('recommended_timeframes', []))}")

                st.markdown("### Actions")
                if st.button("🧪 Backtest This Strategy", use_container_width=True):
                    st.switch_page("pages/2_🧪_Backtest.py")

                if st.button("❌ Close Details"):
                    del st.session_state.selected_strategy
                    st.rerun()

    except Exception as e:
        st.error(f"Failed to load strategy details: {e}")

# Quick stats
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Statistics")
st.sidebar.metric("Total Strategies", len(strategies))
st.sidebar.metric("Filtered", len(filtered_strategies))

# Category breakdown
category_counts = {}
for s in strategies:
    cat = categorize_strategy(s.get('tags', []))
    category_counts[cat] = category_counts.get(cat, 0) + 1

st.sidebar.markdown("### 📂 By Category")
for cat, count in sorted(category_counts.items()):
    st.sidebar.markdown(f"- {cat}: **{count}**")
