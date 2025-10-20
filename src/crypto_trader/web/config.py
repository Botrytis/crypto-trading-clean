"""
Web UI Configuration

Reads API URL from environment variable or uses default localhost.
"""

import os

# API Base URL - can be overridden with API_URL environment variable
API_URL = os.getenv("API_URL", "http://localhost:8001")

# For remote development, set this before starting the web UI:
# export API_URL=http://165.22.71.91:8001
# streamlit run src/crypto_trader/web/app.py
