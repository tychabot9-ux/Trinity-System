#!/bin/bash
# Trinity Command Center v2.0 Launcher
# Enhanced with optimizations, financial projections, and Claude Code integration

echo "🎯 Launching Trinity Command Center v2.0..."

# Navigate to Trinity System directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if required packages are installed
python3 -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Streamlit not found. Installing..."
    pip3 install streamlit
fi

# Launch Command Center v2
echo "🚀 Starting Command Center..."
streamlit run command_center_v2.py --server.port 8001 --server.address localhost

# Keep script running
wait
