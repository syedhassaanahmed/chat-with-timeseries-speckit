#!/bin/bash
set -e

echo "========================================="
echo "Oil Well Time Series API - Dev Container Setup"
echo "========================================="

# Install uv package manager
echo "📦 Installing uv package manager..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Verify uv installation
echo "✓ uv version: $(uv --version)"

# Create virtual environment and install Python dependencies
echo "📦 Creating virtual environment..."
uv venv timeseries-api/.venv --allow-existing
source timeseries-api/.venv/bin/activate

echo "📦 Installing Python dependencies..."
uv pip install -e "timeseries-api/[dev]"

echo "✓ Python dependencies installed"

# Install git hooks
echo "🪝 Installing git hooks..."
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
echo "✓ Git hooks installed"

# Initialize database
echo "🗄️  Initializing database with synthetic data..."
if [ -f "timeseries-api/src/db/seed.py" ]; then
    python timeseries-api/src/db/seed.py
    echo "✓ Database initialized: timeseries-api/data/timeseries.db"
else
    echo "⚠️  Seed script not found yet. Run 'python timeseries-api/src/db/seed.py' manually after implementation."
fi

# Verify installation
echo ""
echo "========================================="
echo "✅ Dev Container setup complete!"
echo "========================================="
echo ""
echo "Quick Start:"
echo "  • Activate environment: source timeseries-api/.venv/bin/activate"
echo "  • Start API server: uvicorn timeseries-api.src.api.main:app --reload --port 8000"
echo "  • View API docs: http://localhost:8000/docs"
echo "  • Run tests: make test"
echo "  • Lint code: make lint"
echo "  • Fix code: make fix"
echo ""
