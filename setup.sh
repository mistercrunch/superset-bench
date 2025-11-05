#!/bin/bash
# Setup script for Apache Superset Benchmark

set -e

echo "🚀 Setting up Apache Superset Benchmark"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Install it with:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✓ uv found"

# Create venv with uv
echo ""
echo "📦 Creating virtual environment..."
uv venv

# Activate venv and install dependencies
echo ""
echo "📦 Installing dependencies..."
source .venv/bin/activate
uv pip install -r requirements.txt

echo ""
echo "✨ Setup complete!"
echo ""
echo "To get started:"
echo "  1. Activate the virtual environment:"
echo "     source .venv/bin/activate"
echo ""
echo "  2. Export your OpenRouter API key:"
echo "     export OPEN_ROUTER_API_KEY='your-key-here'"
echo ""
echo "  3. Run the CLI:"
echo "     python bench.py --help"
echo "     python bench.py models        # List available models"
echo "     python bench.py generate      # Generate questionnaires"
echo "     python bench.py run           # Run benchmark"
echo "     python bench.py results       # View results"
echo ""
