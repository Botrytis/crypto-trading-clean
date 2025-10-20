#!/bin/bash
# Start FastAPI Backend Server

echo "🚀 Starting Crypto Trading API..."
echo "📍 API will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/api/docs"
echo ""

cd "$(dirname "$0")/.." || exit 1

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start API server
uvicorn crypto_trader.api.main:app --reload --port 8000 --host 0.0.0.0
