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

# Install Python dependencies
echo "📦 Installing Python dependencies..."
uv pip install --system -e ".[dev]"

echo "✓ Python dependencies installed"

# Initialize database
echo "🗄️  Initializing database with synthetic data..."
if [ -f "src/db/seed.py" ]; then
    python src/db/seed.py
    echo "✓ Database initialized: data/timeseries.db"
else
    echo "⚠️  Seed script not found yet. Run 'python src/db/seed.py' manually after implementation."
fi

# Verify installation
echo ""
echo "========================================="
echo "✅ Dev Container setup complete!"
echo "========================================="
echo ""
echo "Quick Start:"
echo "  • Start API server: uvicorn src.api.main:app --reload --port 8000"
echo "  • View API docs: http://localhost:8000/docs"
echo "  • Run tests: pytest"
echo "  • Lint code: ruff check src/ tests/"
echo "  • Format code: ruff format src/ tests/"
echo ""
