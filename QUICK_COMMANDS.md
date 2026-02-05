# TRINITY QUICK COMMANDS

**Fast reference for common Trinity operations**

---

## 🎯 MASTER CONTROL

```bash
# Check everything
./trinity_control.sh status

# Start all services
./trinity_control.sh start

# Stop all services
./trinity_control.sh stop

# Restart all
./trinity_control.sh restart

# Run tests
./trinity_control.sh test

# Optimize system
./trinity_control.sh optimize

# Monitor health
./trinity_control.sh monitor

# View logs
./trinity_control.sh logs

# Create backups
./trinity_control.sh backup
```

---

## 🚀 START SERVICES

```bash
# VR Server
python3 vr_server.py

# Command Center
streamlit run command_center.py --server.port 8502 --server.headless true

# Trinity Main API
python3 main.py

# Health Monitor (background)
nohup python3 health_monitor.py > logs/health.out 2>&1 &
```

---

## 🔍 CHECK STATUS

```bash
# Check all ports
lsof -i :8001,8502,8503

# Check specific service
lsof -i :8502  # Command Center
lsof -i :8503  # VR Server
lsof -i :8001  # Trinity API

# Check databases
sqlite3 data/trinity_memory.db "PRAGMA integrity_check;"
sqlite3 job_logs/job_status.db "PRAGMA integrity_check;"

# Check Tailscale
tailscale status

# Check processes
pgrep -f "command_center.py"
pgrep -f "vr_server.py"
pgrep -f "main.py"
```

---

## 🛠️ MAINTENANCE

```bash
# Optimize databases
python3 optimize_system.py

# Clean Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# Backup databases
mkdir -p backups
cp data/trinity_memory.db backups/memory_$(date +%Y%m%d).db
cp job_logs/job_status.db backups/jobs_$(date +%Y%m%d).db

# View disk usage
du -sh cad_output/
du -sh logs/
du -sh backups/
```

---

## 🗄️ DATABASE QUERIES

```bash
# Job statistics
sqlite3 job_logs/job_status.db "SELECT status, COUNT(*) FROM job_statuses GROUP BY status;"

# Recent jobs
sqlite3 job_logs/job_status.db "SELECT company, position, status FROM job_statuses ORDER BY created_date DESC LIMIT 10;"

# Memory stats
python3 -c "from trinity_memory import get_memory; m = get_memory(); print(m.get_memory_stats())"
```

---

## 🌐 ACCESS URLS

```bash
# Desktop
http://localhost:8502  # Command Center
http://localhost:8503  # VR Workspace
http://localhost:8001  # Trinity API

# Quest (Tailscale)
http://100.66.103.8:8502  # Command Center
http://100.66.103.8:8503  # VR Workspace

# Quest (Local WiFi)
http://192.168.1.216:8502  # Command Center
http://192.168.1.216:8503  # VR Workspace
```

---

## 🧪 TESTING

```bash
# Run all tests
python3 test_command_center.py

# View test results
cat TEST_RESULTS.md

# Test VR server
curl http://localhost:8503/api/status

# Test AI
python3 -c "from command_center import generate_scad_code; print(generate_scad_code('cube'))"
```

---

## 📊 MONITORING

```bash
# Live VR server logs
tail -f logs/vr_server.log

# Live Trinity logs
tail -f trinity.log

# Live health monitor
tail -f logs/health_monitor.log

# System resources
top -pid $(pgrep -f "command_center.py")
```

---

## 🔧 TROUBLESHOOTING

```bash
# Kill stuck service
lsof -ti :8502 | xargs kill -9  # Command Center
lsof -ti :8503 | xargs kill -9  # VR Server

# Reset databases (DANGER!)
rm data/trinity_memory.db
rm job_logs/job_status.db
python3 -c "from trinity_memory import get_memory; get_memory()"

# Clear CAD output
rm -rf cad_output/*

# Reinstall dependencies
pip install -r requirements_command_center.txt --force-reinstall
```

---

## 🎮 VR SPECIFIC

```bash
# Check Quest connection
tailscale status | grep -i quest

# Test VR endpoints
curl http://localhost:8503/api/models
curl http://localhost:8503/api/clipboard

# Generate QR code for Quest
python3 quest_setup.py
```

---

## 🤖 AI COMMANDS

```bash
# Test Gemini
python3 -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('OK')"

# Test Claude
python3 -c "import anthropic; print('OK')"

# Test voice
python3 trinity_voice.py
```

---

## 📦 PACKAGE MANAGEMENT

```bash
# List installed packages
pip list | grep -E "streamlit|fastapi|anthropic|google"

# Update packages
pip install --upgrade streamlit fastapi uvicorn anthropic

# Install missing
pip install -r requirements_command_center.txt
```

---

## 🔐 SECURITY

```bash
# Check .env
cat .env | grep -v "^#" | grep -v "^$"

# Verify no exposed keys
grep -r "sk-" --exclude-dir=venv .
grep -r "AIza" --exclude-dir=venv .

# Check file permissions
ls -la .env
ls -la data/trinity_memory.db
```

---

## 🎯 ONE-LINERS

```bash
# Everything status
./trinity_control.sh status

# Full restart
./trinity_control.sh restart

# Quick optimization
./trinity_control.sh optimize

# Emergency stop all
lsof -ti :8001,8502,8503 | xargs kill -9

# Fresh start
./trinity_control.sh stop && sleep 2 && ./trinity_control.sh start

# Test everything
./trinity_control.sh test && cat TEST_RESULTS.md
```

---

## 📱 QUEST SHORTCUTS

Open in Quest Browser:
1. **Main workspace:** `http://100.66.103.8:8503`
2. **Connection test:** `http://100.66.103.8:8503/api/status`
3. **Quest setup:** Scan QR code from `quest_qr_code.png`

---

## 🆘 EMERGENCY COMMANDS

```bash
# Nuclear restart (kills everything)
pkill -f "streamlit|vr_server|main.py"
sleep 2
./trinity_control.sh start

# Reset everything (DANGER - loses data!)
./trinity_control.sh stop
rm -rf data/ job_logs/ cad_output/ logs/
./trinity_control.sh start

# Restore from backup
cp backups/trinity_memory_*.db data/trinity_memory.db
cp backups/job_status_*.db job_logs/job_status.db
```

---

**Remember:** Always backup before destructive operations!

```bash
./trinity_control.sh backup
```
