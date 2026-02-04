#!/bin/bash
# Trinity System Startup Script

cd "$(dirname "$0")"

echo "🔵 Starting Trinity System..."

# Activate virtual environment
source venv/bin/activate

# Start server
python3 main.py
