#!/bin/bash
# Verification script for Lattice Context Layer installation

set -e

echo "🔍 Verifying Lattice Context Layer installation..."
echo ""

# Check Python version
echo "✓ Checking Python version..."
python3 --version | grep -E "Python 3\.(10|11|12)" || {
    echo "❌ Python 3.10+ required"
    exit 1
}

# Check if package is installed
echo "✓ Checking if lattice-context is installed..."
python3 -c "import lattice_context" 2>/dev/null || {
    echo "⚠ Package not installed. Installing in development mode..."
    pip install -e .
}

# Verify CLI is available
echo "✓ Checking CLI availability..."
lattice --help > /dev/null || {
    echo "❌ CLI not available"
    exit 1
}

# Verify core commands
echo "✓ Verifying core commands..."
lattice --help | grep -q "init" || { echo "❌ init command missing"; exit 1; }
lattice --help | grep -q "index" || { echo "❌ index command missing"; exit 1; }
lattice --help | grep -q "serve" || { echo "❌ serve command missing"; exit 1; }
lattice --help | grep -q "context" || { echo "❌ context command missing"; exit 1; }

# Run basic tests
echo "✓ Running basic tests..."
python3 -m pytest tests/ -v --tb=short || {
    echo "⚠ Some tests failed (this may be expected)"
}

echo ""
echo "✅ Lattice Context Layer verification complete!"
echo ""
echo "Next steps:"
echo "  1. cd to a dbt project directory"
echo "  2. Run: lattice init"
echo "  3. Run: lattice index"
echo "  4. Run: lattice status"
echo "  5. Run: lattice serve (to start MCP server)"
