#!/bin/bash
# Trinity VR Server Auto-Restart Script
# Monitors and restarts the VR server if it crashes

VR_DIR="/Users/tybrown/Desktop/Trinity-System"
VR_SCRIPT="$VR_DIR/vr_server.py"
LOG_FILE="$VR_DIR/logs/restart.log"
PID_FILE="$VR_DIR/vr_server.pid"

cd "$VR_DIR" || exit 1

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if server is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Start server
start_server() {
    log "Starting Trinity VR Server..."
    python3 "$VR_SCRIPT" > "$VR_DIR/logs/vr_server.log" 2>&1 &
    echo $! > "$PID_FILE"
    log "Server started with PID $(cat $PID_FILE)"
}

# Stop server
stop_server() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        log "Stopping server (PID: $pid)..."
        kill "$pid" 2>/dev/null
        rm -f "$PID_FILE"
    fi
}

# Main monitoring loop
case "$1" in
    start)
        if is_running; then
            log "Server already running"
            exit 0
        fi
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        sleep 2
        start_server
        ;;
    monitor)
        log "Starting auto-restart monitor..."
        while true; do
            if ! is_running; then
                log "Server not running, restarting..."
                start_server
            fi
            sleep 30
        done
        ;;
    status)
        if is_running; then
            log "Server is running (PID: $(cat $PID_FILE))"
        else
            log "Server is not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|monitor|status}"
        exit 1
        ;;
esac
