#!/bin/bash
# Setup script for MiMo Web3 Research Agent

set -e

echo "🚀 Setting up MiMo Web3 Research Agent..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✓ Python $PYTHON_VERSION detected"

# Create venv
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Create .env if missing
if [ ! -f ".env" ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Edit .env with your API keys before running"
fi

# Create directories
mkdir -p data logs

# Run smoke tests
echo "🧪 Running smoke tests..."
python tests/test_smoke.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys (MIMO_API_KEY, TELEGRAM_BOT_TOKEN, etc.)"
echo "2. Edit config.yaml to set wallets/channels to monitor"
echo "3. Run: python -m src.bot"
echo ""
