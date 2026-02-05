#!/bin/bash
# Trinity Autonomous VR Deployment
# Runs while user is AFK

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔════════════════════════════════════════════════════════╗"
echo "║      TRINITY VR AUTONOMOUS DEPLOYMENT                  ║"
echo "║      Working while you're AFK...                       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Ensure directories exist
mkdir -p logs
mkdir -p cad_output

# Get network info
get_local_ip() {
    python3 -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); print(s.getsockname()[0]); s.close()" 2>/dev/null || echo "Not available"
}

get_tailscale_ip() {
    tailscale ip -4 2>/dev/null || echo "Not available"
}

LOCAL_IP=$(get_local_ip)
TAILSCALE_IP=$(get_tailscale_ip)

echo "🌐 Network Configuration:"
echo "   Local WiFi IP:  $LOCAL_IP"
echo "   Tailscale IP:   $TAILSCALE_IP"
echo ""

# Check if server is already running
if lsof -Pi :8503 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ VR server already running on port 8503"
    SERVER_PID=$(lsof -Pi :8503 -sTCP:LISTEN -t)
    echo "   Server PID: $SERVER_PID"
else
    echo "📡 Starting VR server (wireless mode)..."
    python3 vr_server.py > logs/vr_server_stdout.log 2>&1 &
    SERVER_PID=$!
    echo $SERVER_PID > vr_server.pid

    # Wait for server to start
    sleep 3

    # Verify server started
    if lsof -Pi :8503 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "✅ VR server started successfully"
        echo "   Server PID: $SERVER_PID"
    else
        echo "❌ Failed to start VR server"
        echo "   Check logs: logs/vr_server_stdout.log"
        exit 1
    fi
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║                 ACCESS INFORMATION                     ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

if [ "$LOCAL_IP" != "Not available" ]; then
    echo "📱 Local WiFi Access (RECOMMENDED):"
    echo "   URL: http://$LOCAL_IP:8503/vr"
    echo "   Use this for lowest latency"
    echo ""
fi

if [ "$TAILSCALE_IP" != "Not available" ]; then
    echo "🔐 Tailscale VPN Access:"
    echo "   URL: http://$TAILSCALE_IP:8503/vr"
    echo "   Use this for remote access"
    echo ""
fi

echo "🖥️  Localhost Access (Mac only):"
echo "   URL: http://localhost:8503/vr"
echo ""

echo "╔════════════════════════════════════════════════════════╗"
echo "║              OCULUS QUEST 1 INSTRUCTIONS               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "1. Put on your Oculus Quest 1"
echo "2. Press Oculus button to open menu"
echo "3. Select 'Browser'"
echo "4. Navigate to: http://$LOCAL_IP:8503/vr"
echo "5. Click 'DEPLOY TO VR' button"
echo "6. Grant VR permissions when prompted"
echo "7. Start using the tactical workspace!"
echo ""

echo "╔════════════════════════════════════════════════════════╗"
echo "║                   API ENDPOINTS                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Status:    http://$LOCAL_IP:8503/api/status"
echo "Models:    http://$LOCAL_IP:8503/api/models"
echo "Generate:  http://$LOCAL_IP:8503/api/generate_cad (POST)"
echo ""

echo "╔════════════════════════════════════════════════════════╗"
echo "║                   SYSTEM STATUS                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Test server status
if curl -s http://localhost:8503/api/status > /dev/null 2>&1; then
    echo "✅ Server responding to requests"

    # Show server stats
    STATUS=$(curl -s http://localhost:8503/api/status)
    echo ""
    echo "Server Stats:"
    echo "$STATUS" | python3 -m json.tool 2>/dev/null || echo "$STATUS"
else
    echo "⚠️  Server not responding yet (may still be starting)"
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║                   LOGS & MONITORING                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📝 Server logs:     logs/vr_server.log"
echo "📝 Stdout logs:     logs/vr_server_stdout.log"
echo "📝 Stderr logs:     logs/vr_server_stderr.log"
echo ""
echo "💡 View live logs:  tail -f logs/vr_server.log"
echo "💡 Test endpoint:   curl http://localhost:8503/api/status"
echo "💡 Restart server:  ./restart_vr_server.sh restart"
echo "💡 Stop server:     ./restart_vr_server.sh stop"
echo ""

echo "╔════════════════════════════════════════════════════════╗"
echo "║                   QUICK REFERENCE                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "🎯 Shooting Range Targets:"
echo "   - Left: ROTATE tool"
echo "   - Center: SCALE tool"
echo "   - Right: MOVE tool"
echo ""
echo "🎮 Controller Buttons:"
echo "   - Trigger: Shoot/Select"
echo "   - B/Y: Toggle radial menu"
echo "   - A/X: Quick tool cycle"
echo "   - Grip: Grab model"
echo ""
echo "📚 Documentation:"
echo "   - Interface Guide:  VR_SHOOTING_RANGE_DOCS.md"
echo "   - Quest Setup:      QUEST_SETUP_GUIDE.md"
echo "   - Server Code:      vr_server.py"
echo ""

echo "╔════════════════════════════════════════════════════════╗"
echo "║                    ALL SYSTEMS GO                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "🤖 Trinity VR Workspace is ready!"
echo "🥽 Put on your Quest and connect now"
echo ""
echo "Press Ctrl+C to stop following logs (server keeps running)"
echo "Or run './restart_vr_server.sh stop' to stop server"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# Follow logs if server was just started
if [ ! -z "$SERVER_PID" ] && ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "Following server logs (Ctrl+C to exit)..."
    echo ""
    tail -f logs/vr_server.log 2>/dev/null || tail -f logs/vr_server_stdout.log
fi
