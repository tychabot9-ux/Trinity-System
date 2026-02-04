#!/bin/bash
# Trinity Command Center - Unified Launch Script

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         TRINITY COMMAND CENTER - LAUNCH SEQUENCE               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Change to Trinity directory
cd "$(dirname "$0")"

# Check if dependencies are installed
echo "🔍 Checking dependencies..."

# Check Python packages
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip3 install -r requirements_command_center.txt
else
    echo "✅ Python dependencies OK"
fi

# Check OpenSCAD
if ! command -v openscad &> /dev/null; then
    echo "⚠️  OpenSCAD not found. Installing..."
    echo "   Running: brew install --cask openscad"
    brew install --cask openscad
else
    echo "✅ OpenSCAD installed"
fi

echo ""
echo "🚀 Starting Trinity Command Center..."
echo ""

# Set environment
export TRINITY_API_BASE="http://localhost:8001"

# Check if Trinity API is already running
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "✅ Trinity API already running on port 8001"
    echo ""
    echo "🎯 Launching Command Center in standalone mode..."
    echo "   Access at: http://localhost:8502"
    echo ""
    streamlit run command_center.py \
        --server.port=8502 \
        --server.address=0.0.0.0 \
        --theme.base=dark \
        --theme.primaryColor="#00FF00" \
        --theme.backgroundColor="#0E1117"
else
    echo "⚠️  Trinity API not running. Starting integrated mode..."
    echo ""
    python3 trinity_command_mount.py
fi
