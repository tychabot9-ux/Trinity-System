#!/bin/bash
# Trinity VR Workspace Launcher
# Starts VR server for Oculus Quest 1

echo "╔════════════════════════════════════════╗"
echo "║   TRINITY VR WORKSPACE LAUNCHER        ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check if Oculus Quest is connected
if system_profiler SPUSBDataType | grep -q "Quest"; then
    echo "✅ Oculus Quest 1 detected"
else
    echo "⚠️  Oculus Quest 1 not detected"
    echo "   Please connect via USB-C cable"
    echo ""
fi

# Check for CAD output directory
if [ ! -d "cad_output" ]; then
    echo "📁 Creating CAD output directory..."
    mkdir -p cad_output
fi

# Copy test model if it exists
if [ -f "/tmp/test_bolt.scad" ]; then
    echo "📦 Test model found, preparing..."
fi

# Get local IP address for Quest access
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

echo ""
echo "🚀 Starting Trinity VR Server..."
echo ""
echo "🌐 Access URLs:"
echo "   Desktop: http://localhost:8503/vr"
echo "   Quest:   http://$LOCAL_IP:8503/vr"
echo ""
echo "🎮 Oculus Quest 1 Setup:"
echo "   1. Put on your Quest 1 headset"
echo "   2. Open Oculus Browser"
echo "   3. Navigate to: http://$LOCAL_IP:8503/vr"
echo "   4. Allow VR permissions when prompted"
echo "   5. Click 'ENTER VR' button"
echo ""
echo "🎯 Controls:"
echo "   🅰️  Button - Rotate mode"
echo "   🅱️  Button - Reset view"
echo "   Grip    - Grab & move model"
echo "   Trigger - Select tools/models"
echo ""
echo "Press Ctrl+C to stop the server"
echo "════════════════════════════════════════"
echo ""

# Start VR server
python3 vr_server.py
