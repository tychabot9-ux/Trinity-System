#!/bin/bash
# Trinity VR Server Monitoring Script
# Real-time monitoring and performance tracking

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_FILE="logs/monitor.log"
ALERT_LOG="logs/alerts.log"

mkdir -p logs

# Colors for terminal output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

alert() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ALERT: $1" | tee -a "$ALERT_LOG"
}

# Get server stats
get_stats() {
    curl -s http://localhost:8503/api/status 2>/dev/null
}

# Check if server is running
is_running() {
    lsof -Pi :8503 -sTCP:LISTEN -t >/dev/null 2>&1
}

# Get process info
get_process_info() {
    if [ -f vr_server.pid ]; then
        PID=$(cat vr_server.pid)
        if ps -p $PID > /dev/null 2>&1; then
            # CPU usage
            CPU=$(ps -p $PID -o %cpu | tail -1 | tr -d ' ')
            # Memory usage
            MEM=$(ps -p $PID -o rss | tail -1 | tr -d ' ')
            MEM_MB=$((MEM / 1024))

            echo "CPU: ${CPU}% | Memory: ${MEM_MB}MB"
        else
            echo "Process not found"
        fi
    else
        echo "PID file not found"
    fi
}

# Monitor mode
monitor_mode() {
    clear
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║        TRINITY VR SERVER MONITORING                    ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "Press Ctrl+C to exit"
    echo ""

    while true; do
        clear
        echo "╔════════════════════════════════════════════════════════╗"
        echo "║        TRINITY VR SERVER MONITORING                    ║"
        echo "║        $(date '+%Y-%m-%d %H:%M:%S')                         ║"
        echo "╚════════════════════════════════════════════════════════╝"
        echo ""

        # Server status
        if is_running; then
            echo -e "${GREEN}✅ Server Status: ONLINE${NC}"
        else
            echo -e "${RED}❌ Server Status: OFFLINE${NC}"
            echo ""
            echo "Run './restart_vr_server.sh start' to start server"
            sleep 5
            continue
        fi

        echo ""

        # Process info
        echo "📊 Process Information:"
        PROC_INFO=$(get_process_info)
        echo "   $PROC_INFO"
        echo ""

        # API stats
        echo "🌐 Server Statistics:"
        STATS=$(get_stats)

        if [ -n "$STATS" ]; then
            UPTIME=$(echo "$STATS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('uptime_human', 'N/A'))" 2>/dev/null)
            REQUESTS=$(echo "$STATS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('requests', 'N/A'))" 2>/dev/null)
            MODELS=$(echo "$STATS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('models_count', 'N/A'))" 2>/dev/null)
            LOCAL_IP=$(echo "$STATS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('network', {}).get('local', 'N/A'))" 2>/dev/null)
            TAILSCALE_IP=$(echo "$STATS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('network', {}).get('tailscale', 'N/A'))" 2>/dev/null)

            echo "   Uptime:        $UPTIME"
            echo "   Requests:      $REQUESTS"
            echo "   Models:        $MODELS"
            echo ""
            echo "   Local IP:      $LOCAL_IP"
            echo "   Tailscale IP:  $TAILSCALE_IP"
        else
            echo -e "   ${YELLOW}⚠️  Unable to fetch stats${NC}"
        fi

        echo ""

        # Network status
        echo "📡 Network Status:"
        if ping -c 1 -W 1 8.8.8.8 > /dev/null 2>&1; then
            echo -e "   ${GREEN}✅ Internet: Connected${NC}"
        else
            echo -e "   ${RED}❌ Internet: Disconnected${NC}"
        fi

        if tailscale status > /dev/null 2>&1; then
            echo -e "   ${GREEN}✅ Tailscale: Active${NC}"
        else
            echo -e "   ${YELLOW}⚠️  Tailscale: Not available${NC}"
        fi

        echo ""

        # Recent logs
        echo "📝 Recent Activity (last 5 lines):"
        if [ -f logs/vr_server.log ]; then
            tail -5 logs/vr_server.log | sed 's/^/   /'
        else
            echo "   No logs available"
        fi

        echo ""
        echo "════════════════════════════════════════════════════════════"
        echo "Next update in 5 seconds... (Ctrl+C to exit)"

        sleep 5
    done
}

# Performance report
performance_report() {
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║        TRINITY VR PERFORMANCE REPORT                   ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""

    if ! is_running; then
        echo "❌ Server is not running"
        exit 1
    fi

    STATS=$(get_stats)

    if [ -z "$STATS" ]; then
        echo "❌ Unable to fetch server stats"
        exit 1
    fi

    echo "📊 Server Performance:"
    echo "$STATS" | python3 -m json.tool 2>/dev/null
    echo ""

    echo "💾 Process Resources:"
    get_process_info
    echo ""

    echo "📁 Disk Usage:"
    du -sh cad_output 2>/dev/null | awk '{print "   CAD Output: " $1}'
    du -sh logs 2>/dev/null | awk '{print "   Logs: " $1}'
    echo ""

    echo "📝 Log Files:"
    ls -lh logs/*.log 2>/dev/null | awk '{print "   " $9 ": " $5}' || echo "   No log files"
    echo ""

    echo "✅ Report complete"
}

# Usage
case "$1" in
    monitor)
        monitor_mode
        ;;
    report)
        performance_report
        ;;
    stats)
        if is_running; then
            echo "Server Stats:"
            get_stats | python3 -m json.tool 2>/dev/null
        else
            echo "Server is not running"
        fi
        ;;
    process)
        if is_running; then
            echo "Process Info:"
            get_process_info
        else
            echo "Server is not running"
        fi
        ;;
    *)
        echo "Trinity VR Server Monitoring"
        echo ""
        echo "Usage: $0 {monitor|report|stats|process}"
        echo ""
        echo "  monitor  - Real-time monitoring dashboard"
        echo "  report   - Generate performance report"
        echo "  stats    - Show server statistics"
        echo "  process  - Show process information"
        echo ""
        exit 1
        ;;
esac
