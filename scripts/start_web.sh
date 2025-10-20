#!/bin/bash
# Start Streamlit Web UI

echo "🌐 Starting Crypto Trading Web UI..."
echo "📍 UI will be available at: http://localhost:8501"
echo ""
echo "⚠️  Make sure API is running first!"
echo "   Run: ./scripts/start_api.sh (in another terminal)"
echo ""

cd "$(dirname "$0")/.." || exit 1

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start Streamlit
streamlit run src/crypto_trader/web/app.py
