#!/bin/bash
# Setup script for Crypto Trading Platform
# Creates virtual environment and installs all dependencies

set -e  # Exit on error

echo "🚀 Setting up Crypto Trading Platform..."
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $python_version"
echo ""

# Create virtual environment
echo "🔨 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Remove it? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        rm -rf venv
        echo "✅ Removed old virtual environment"
    else
        echo "ℹ️  Using existing virtual environment"
    fi
fi

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip
echo "✅ pip upgraded"
echo ""

# Install dependencies
echo "📚 Installing dependencies from requirements.txt..."
echo "⏳ This may take 5-10 minutes..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Install package in development mode
echo "🔧 Installing crypto-trader package in development mode..."
pip install -e .
echo "✅ Package installed"
echo ""

# Verify installation
echo "✔️  Verifying installation..."
python -c "from crypto_trader.api.main import app; print('✅ crypto_trader module imports successfully')"
echo ""

# Success message
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Start the API server (Terminal 1):"
echo "   ./scripts/start_api.sh"
echo ""
echo "3. Start the Web UI (Terminal 2):"
echo "   ./scripts/start_web.sh"
echo ""
echo "4. Open your browser:"
echo "   http://localhost:8501"
echo ""
echo "📖 Documentation:"
echo "   - API Docs: http://localhost:8001/api/docs"
echo "   - README: See README.md"
echo "   - Phase 1 Report: See PHASE1_COMPLETE.md"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
