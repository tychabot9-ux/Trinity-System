#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# TRINITY SYSTEM MASTER CONTROL
# All-in-one system management script
# ═══════════════════════════════════════════════════════════════

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Directory
TRINITY_DIR="/Users/tybrown/Desktop/Trinity-System"
cd "$TRINITY_DIR" || exit 1

# Banner
show_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║              TRINITY SYSTEM MASTER CONTROL                     ║"
    echo "║              Personal AI Operating System                      ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Status check
check_status() {
    echo -e "${BLUE}Checking Trinity system status...${NC}\n"

    # Check services
    echo -e "${YELLOW}Services:${NC}"

    if lsof -i :8502 > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅${NC} Command Center (8502) - RUNNING"
    else
        echo -e "  ${RED}❌${NC} Command Center (8502) - STOPPED"
    fi

    if lsof -i :8503 > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅${NC} VR Server (8503) - RUNNING"
    else
        echo -e "  ${RED}❌${NC} VR Server (8503) - STOPPED"
    fi

    if lsof -i :8001 > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅${NC} Trinity API (8001) - RUNNING"
    else
        echo -e "  ${YELLOW}⚠️${NC}  Trinity API (8001) - STOPPED"
    fi

    # Check databases
    echo -e "\n${YELLOW}Databases:${NC}"

    if [ -f "data/trinity_memory.db" ]; then
        size=$(du -h data/trinity_memory.db | cut -f1)
        echo -e "  ${GREEN}✅${NC} Trinity Memory DB ($size)"
    else
        echo -e "  ${RED}❌${NC} Trinity Memory DB - MISSING"
    fi

    if [ -f "job_logs/job_status.db" ]; then
        size=$(du -h job_logs/job_status.db | cut -f1)
        echo -e "  ${GREEN}✅${NC} Job Status DB ($size)"
    else
        echo -e "  ${RED}❌${NC} Job Status DB - MISSING"
    fi

    # Check network
    echo -e "\n${YELLOW}Network:${NC}"

    if command -v tailscale > /dev/null; then
        tailscale_ip=$(tailscale ip -4 2>/dev/null)
        if [ -n "$tailscale_ip" ]; then
            echo -e "  ${GREEN}✅${NC} Tailscale - $tailscale_ip"
        else
            echo -e "  ${RED}❌${NC} Tailscale - Not connected"
        fi
    else
        echo -e "  ${YELLOW}⚠️${NC}  Tailscale - Not installed"
    fi
}

# Start all services
start_all() {
    echo -e "${BLUE}Starting Trinity services...${NC}\n"

    # VR Server
    if ! lsof -i :8503 > /dev/null 2>&1; then
        echo -e "${YELLOW}Starting VR Server...${NC}"
        python3 vr_server.py > /dev/null 2>&1 &
        sleep 2
        echo -e "${GREEN}✅ VR Server started${NC}"
    else
        echo -e "${CYAN}VR Server already running${NC}"
    fi

    # Command Center
    if ! lsof -i :8502 > /dev/null 2>&1; then
        echo -e "${YELLOW}Starting Command Center...${NC}"
        streamlit run command_center.py --server.port 8502 --server.headless true --browser.gatherUsageStats false > /dev/null 2>&1 &
        sleep 3
        echo -e "${GREEN}✅ Command Center started${NC}"
    else
        echo -e "${CYAN}Command Center already running${NC}"
    fi

    echo -e "\n${GREEN}Services started!${NC}"
    echo -e "${CYAN}Access URLs:${NC}"
    echo -e "  Command Center: ${BLUE}http://localhost:8502${NC}"
    echo -e "  VR Workspace:   ${BLUE}http://localhost:8503${NC}"
}

# Stop all services
stop_all() {
    echo -e "${BLUE}Stopping Trinity services...${NC}\n"

    # Kill by port
    if lsof -i :8502 > /dev/null 2>&1; then
        lsof -ti :8502 | xargs kill -9 2>/dev/null
        echo -e "${GREEN}✅ Command Center stopped${NC}"
    fi

    if lsof -i :8503 > /dev/null 2>&1; then
        lsof -ti :8503 | xargs kill -9 2>/dev/null
        echo -e "${GREEN}✅ VR Server stopped${NC}"
    fi

    if lsof -i :8001 > /dev/null 2>&1; then
        lsof -ti :8001 | xargs kill -9 2>/dev/null
        echo -e "${GREEN}✅ Trinity API stopped${NC}"
    fi

    echo -e "\n${GREEN}All services stopped${NC}"
}

# Restart services
restart_all() {
    stop_all
    sleep 2
    start_all
}

# Run tests
run_tests() {
    echo -e "${BLUE}Running Trinity test suite...${NC}\n"
    python3 test_command_center.py

    if [ -f "TEST_RESULTS.md" ]; then
        echo -e "\n${GREEN}✅ Test results saved to TEST_RESULTS.md${NC}"
    fi
}

# Optimize system
optimize() {
    echo -e "${BLUE}Optimizing Trinity system...${NC}\n"
    python3 optimize_system.py
}

# Health monitor
health_monitor() {
    echo -e "${BLUE}Starting health monitor...${NC}\n"
    python3 health_monitor.py
}

# Show logs
show_logs() {
    echo -e "${BLUE}Recent Trinity logs:${NC}\n"

    if [ -f "logs/vr_server.log" ]; then
        echo -e "${YELLOW}=== VR Server (last 10 lines) ===${NC}"
        tail -10 logs/vr_server.log
        echo ""
    fi

    if [ -f "trinity.log" ]; then
        echo -e "${YELLOW}=== Trinity Main (last 10 lines) ===${NC}"
        tail -10 trinity.log
        echo ""
    fi
}

# Backup databases
backup() {
    echo -e "${BLUE}Creating Trinity backups...${NC}\n"

    timestamp=$(date +%Y%m%d_%H%M%S)
    mkdir -p backups

    if [ -f "data/trinity_memory.db" ]; then
        cp data/trinity_memory.db "backups/trinity_memory_$timestamp.db"
        echo -e "${GREEN}✅ Memory DB backed up${NC}"
    fi

    if [ -f "job_logs/job_status.db" ]; then
        cp job_logs/job_status.db "backups/job_status_$timestamp.db"
        echo -e "${GREEN}✅ Job Status DB backed up${NC}"
    fi

    echo -e "\n${GREEN}Backups saved to: backups/${NC}"
}

# Show help
show_help() {
    echo -e "${YELLOW}Usage:${NC} ./trinity_control.sh [command]"
    echo ""
    echo -e "${CYAN}Commands:${NC}"
    echo -e "  ${GREEN}status${NC}       - Check system status"
    echo -e "  ${GREEN}start${NC}        - Start all services"
    echo -e "  ${GREEN}stop${NC}         - Stop all services"
    echo -e "  ${GREEN}restart${NC}      - Restart all services"
    echo -e "  ${GREEN}test${NC}         - Run comprehensive tests"
    echo -e "  ${GREEN}optimize${NC}     - Optimize databases and clean up"
    echo -e "  ${GREEN}monitor${NC}      - Start health monitoring (Ctrl+C to stop)"
    echo -e "  ${GREEN}logs${NC}         - Show recent logs"
    echo -e "  ${GREEN}backup${NC}       - Create database backups"
    echo -e "  ${GREEN}help${NC}         - Show this help message"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo -e "  ./trinity_control.sh status"
    echo -e "  ./trinity_control.sh restart"
    echo -e "  ./trinity_control.sh test"
}

# Main logic
main() {
    show_banner

    case "$1" in
        status)
            check_status
            ;;
        start)
            start_all
            ;;
        stop)
            stop_all
            ;;
        restart)
            restart_all
            ;;
        test)
            run_tests
            ;;
        optimize)
            optimize
            ;;
        monitor)
            health_monitor
            ;;
        logs)
            show_logs
            ;;
        backup)
            backup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            if [ -n "$1" ]; then
                echo -e "${RED}Unknown command: $1${NC}\n"
            fi
            show_help
            exit 1
            ;;
    esac
}

# Run main
main "$@"
