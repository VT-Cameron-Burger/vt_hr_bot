#!/usr/bin/env bash
set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting VT HR Bot Server..."
echo "📁 Project root: $PROJECT_ROOT"

# Change to project root
cd "$PROJECT_ROOT"

# Check if .venv exists
if [ ! -f .venv/bin/activate ]; then
    echo "❌ Virtual environment not found at .venv"
    echo "💡 Create it with: python3 -m venv .venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Verify Python dependencies
echo "📦 Checking dependencies..."
if ! python -c "import load_data, ui.server" 2>/dev/null; then
    echo "❌ Missing dependencies. Install with:"
    echo "   source .venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Check for vector database
if [ ! -f pdf_vectors.pkl ]; then
    echo "⚠️  Vector database not found. Creating..."
    python load_data.py
fi

# Default port
PORT=${1:-8000}

echo "🌐 Starting server on port $PORT..."
echo "📊 Loading vector database..."

# Start the server with exec to replace the shell process
exec python ui/server.py --port "$PORT"