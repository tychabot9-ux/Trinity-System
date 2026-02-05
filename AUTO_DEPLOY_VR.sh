#!/bin/bash
# Trinity Autonomous VR Deployment
# Runs while user is AFK

echo "🤖 TRINITY AUTONOMOUS MODE ACTIVATED"
echo "Working while you're away..."
echo ""

# Start VR server
echo "📡 Starting VR server (wireless)..."
python3 vr_server.py > /tmp/vr_server.log 2>&1 &
VR_PID=$!

sleep 3

# Get network info
TAILSCALE_IP=$(tailscale ip -4 2>/dev/null)
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

echo ""
echo "✅ VR Workspace Deployed"
echo ""
echo "🌐 Access URLs:"
echo "   Tailscale: http://$TAILSCALE_IP:8503/vr"
echo "   Local WiFi: http://$LOCAL_IP:8503/vr"
echo ""
echo "🥽 Oculus Quest 1 Instructions:"
echo "   1. Open Oculus Browser on Quest"
echo "   2. Navigate to: http://$LOCAL_IP:8503/vr"
echo "   3. Click 'DEPLOY TO VR'"
echo ""
echo "🤖 Trinity is auto-optimizing..."
echo "   Server PID: $VR_PID"
echo "   Logs: /tmp/vr_server.log"
echo ""
echo "Press Ctrl+C to stop (or leave running while AFK)"

# Keep running
tail -f /tmp/vr_server.log
