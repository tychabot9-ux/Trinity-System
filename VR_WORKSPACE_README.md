# Trinity VR Wireless Workspace
## Complete Setup and Operation Guide

### System Overview

The Trinity VR Wireless Workspace is a Call of Duty-inspired tactical engineering interface for Oculus Quest 1, featuring:

- **COD-Style Shooting Range**: Select tools by shooting targets
- **Tactical HUD**: Military-themed heads-up display
- **Radial Menu**: Weapon wheel-inspired quick actions
- **Wireless Operation**: WiFi and Tailscale VPN support
- **Auto-Optimization**: Performance monitoring and adjustment
- **CAD Integration**: Generate and manipulate 3D models in VR

---

## Quick Start (5 Minutes)

### 1. Start the Server
```bash
cd /Users/tybrown/Desktop/Trinity-System
./AUTO_DEPLOY_VR.sh
```

### 2. Connect Quest 1
1. Put on Oculus Quest 1
2. Open Oculus Browser
3. Navigate to displayed URL (e.g., `http://192.168.1.216:8503/vr`)
4. Click "DEPLOY TO VR"
5. Start creating!

---

## File Structure

### Core Files
```
vr_server.py                    - Python HTTP server with API endpoints
vr_workspace_wireless.html      - VR interface (A-Frame WebXR)
AUTO_DEPLOY_VR.sh              - One-command deployment script
```

### Management Scripts
```
restart_vr_server.sh           - Auto-restart and monitoring
monitor_vr.sh                  - Real-time performance dashboard
configure_firewall.sh          - macOS firewall configuration
test_endpoints.sh              - API endpoint testing
generate_qr_code.py            - QR code generator for Quest
```

### Configuration Files
```
com.trinity.vr.plist           - LaunchDaemon for auto-start
verify_firewall.sh             - Firewall verification
```

### Documentation
```
VR_SHOOTING_RANGE_DOCS.md      - Interface documentation (this file)
QUEST_SETUP_GUIDE.md           - Quest setup instructions
VR_WORKSPACE_README.md         - Overall system guide
```

### Directories
```
logs/                          - Server logs and monitoring data
cad_output/                    - Generated CAD models (.stl, .gltf)
```

---

## Network Configuration

### Option 1: Local WiFi (Recommended)
- **URL**: `http://192.168.1.216:8503/vr`
- **Latency**: < 20ms (excellent)
- **Range**: Within WiFi coverage
- **Setup**: Both devices on same network

### Option 2: Tailscale VPN
- **URL**: `http://100.66.103.8:8503/vr`
- **Latency**: 20-50ms (good)
- **Range**: Anywhere with internet
- **Setup**: Tailscale installed on both devices

### Firewall Configuration
```bash
# Check if firewall is blocking connections
sudo ./configure_firewall.sh

# Verify configuration
./verify_firewall.sh
```

---

## Management Commands

### Server Control
```bash
# Start server
./AUTO_DEPLOY_VR.sh

# Restart server
./restart_vr_server.sh restart

# Stop server
./restart_vr_server.sh stop

# Check status
./restart_vr_server.sh status

# Auto-restart monitoring (keeps server alive)
./restart_vr_server.sh monitor
```

### Monitoring
```bash
# Real-time dashboard
./monitor_vr.sh monitor

# Performance report
./monitor_vr.sh report

# Server stats
./monitor_vr.sh stats

# Process info
./monitor_vr.sh process
```

### Testing
```bash
# Test all endpoints
./test_endpoints.sh

# Test specific endpoint
curl http://localhost:8503/api/status

# Generate QR codes for Quest
python3 generate_qr_code.py
```

### Logs
```bash
# View live server logs
tail -f logs/vr_server.log

# View all logs
ls -lh logs/

# Clear old logs
rm logs/*.log
```

---

## API Endpoints

### GET /vr
Main VR workspace interface
```bash
curl http://localhost:8503/vr
```

### GET /api/status
Server health and statistics
```bash
curl http://localhost:8503/api/status
```

**Response**:
```json
{
  "status": "online",
  "uptime": 3600,
  "uptime_human": "1h 0m",
  "requests": 127,
  "models_count": 5,
  "timestamp": "2026-02-04T12:00:00",
  "version": "1.0",
  "wireless": true,
  "network": {
    "tailscale": "100.66.103.8",
    "local": "192.168.1.216"
  }
}
```

### GET /api/models
List available CAD models
```bash
curl http://localhost:8503/api/models
```

**Response**:
```json
[
  {
    "name": "bolt_m8.stl",
    "path": "/cad_output/bolt_m8.stl",
    "size": 1048576,
    "modified": 1706918400.0
  }
]
```

### POST /api/generate_cad
Generate new CAD model
```bash
curl -X POST http://localhost:8503/api/generate_cad \
  -H "Content-Type: application/json" \
  -d '{"prompt":"M8 hex bolt"}'
```

**Response**:
```json
{
  "status": "success",
  "filename": "test_bolt.stl",
  "message": "Generating: M8 hex bolt",
  "timestamp": "2026-02-04T12:00:00"
}
```

---

## VR Interface Guide

### Shooting Range (Tool Selection)
Point controller at target and pull trigger to select:
- **Left Target**: ROTATE tool
- **Center Target**: SCALE tool
- **Right Target**: MOVE tool

### Controller Layout

#### Left Controller
- **Y Button**: Toggle radial menu
- **X Button**: Quick tool cycle
- **Grip**: Grab object
- **Trigger**: Shoot/select
- **Thumbstick**: Movement

#### Right Controller
- **B Button**: Toggle radial menu
- **A Button**: Quick action
- **Grip**: Grab object
- **Trigger**: Shoot/select
- **Thumbstick**: Movement

### Radial Menu (Press Y or B)
- **GEN**: Generate new model
- **LOAD**: Load existing model
- **SAVE**: Save current model
- **DELETE**: Delete model
- **EXPORT**: Export to file
- **SETTINGS**: Open settings
- **TOOLS**: Tool menu
- **HOME**: Return to home

### HUD Elements
- **Top Right**: Status and tool info
- **Bottom Right**: Model counter
- **Bottom Left**: Minimap
- **Center**: Crosshair

---

## Performance Optimization

### Server Optimization
- Auto-adjusts rendering quality
- Monitors frame rate (target: 72 FPS for Quest 1)
- Network connection monitoring
- Resource usage tracking

### Network Optimization
- Use 5GHz WiFi (not 2.4GHz)
- Keep Quest within 10m of router
- Minimize network traffic during use
- Consider dedicated VR network

### Quest Settings
- Clear Guardian boundary
- Good room lighting
- Fresh controller batteries
- Clean lenses

---

## Auto-Start Configuration

### Using LaunchDaemon (macOS)

1. **Copy plist file**:
```bash
sudo cp com.trinity.vr.plist /Library/LaunchDaemons/
sudo chown root:wheel /Library/LaunchDaemons/com.trinity.vr.plist
```

2. **Load service**:
```bash
sudo launchctl load /Library/LaunchDaemons/com.trinity.vr.plist
```

3. **Start service**:
```bash
sudo launchctl start com.trinity.vr
```

4. **Check status**:
```bash
sudo launchctl list | grep trinity
```

5. **Stop service**:
```bash
sudo launchctl stop com.trinity.vr
```

6. **Unload service**:
```bash
sudo launchctl unload /Library/LaunchDaemons/com.trinity.vr.plist
```

---

## Troubleshooting

### Server Won't Start
```bash
# Check if port is in use
lsof -i :8503

# Kill process on port
kill $(lsof -t -i :8503)

# Check logs
tail -f logs/vr_server.log
```

### Quest Can't Connect
```bash
# Test from Mac
curl http://localhost:8503/api/status

# Test endpoints
./test_endpoints.sh

# Check firewall
./verify_firewall.sh
sudo ./configure_firewall.sh

# Verify network
ping 192.168.1.216
```

### Low Performance
```bash
# Check server resources
./monitor_vr.sh process

# View performance report
./monitor_vr.sh report

# Reduce model complexity
# Move closer to router
# Close other applications
```

### Connection Lost
```bash
# Check server status
./restart_vr_server.sh status

# Restart server
./restart_vr_server.sh restart

# Monitor in real-time
./monitor_vr.sh monitor
```

---

## Development

### Adding New Endpoints

Edit `vr_server.py`:
```python
def do_GET(self):
    if parsed_path.path == '/api/my_endpoint':
        # Handle request
        response = {'data': 'value'}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
        return
```

### Customizing VR Interface

Edit `vr_workspace_wireless.html`:
```html
<!-- Add new target -->
<a-entity class="target" data-tool="custom" position="4 0 0">
    <a-circle radius="0.4" color="#0c0"></a-circle>
    <a-text value="CUSTOM" align="center" color="#0f0"></a-text>
</a-entity>
```

### Adding Tools

In `vr_workspace_wireless.html`:
```javascript
function customTool() {
    currentTool = 'custom';
    updateHUD('CUSTOM TOOL', 'custom', modelCount);
    // Tool logic here
}
```

---

## Security

### Best Practices
- Only allow connections from trusted networks
- Use Tailscale VPN for remote access
- Keep firewall enabled when not in VR
- Monitor logs for suspicious activity
- Don't expose server to public internet

### Network Security
```bash
# Check firewall status
defaults read /Library/Preferences/com.apple.alf globalstate

# View firewall apps
/usr/libexec/ApplicationFirewall/socketfilterfw --listapps

# Enable stealth mode (optional)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on
```

---

## Maintenance

### Daily
- Check server status
- View recent logs
- Test endpoints

### Weekly
- Review performance reports
- Clean old logs
- Update Quest firmware
- Check for updates

### Monthly
- Full system test
- Backup CAD files
- Review security logs
- Update documentation

---

## Support Resources

### Documentation
- Interface Guide: `VR_SHOOTING_RANGE_DOCS.md`
- Quest Setup: `QUEST_SETUP_GUIDE.md`
- This File: `VR_WORKSPACE_README.md`

### Logs
- Server logs: `logs/vr_server.log`
- Monitor logs: `logs/monitor.log`
- Alert logs: `logs/alerts.log`

### Commands Quick Reference
```bash
# Start
./AUTO_DEPLOY_VR.sh

# Monitor
./monitor_vr.sh monitor

# Test
./test_endpoints.sh

# Restart
./restart_vr_server.sh restart

# Logs
tail -f logs/vr_server.log
```

---

## Performance Targets

### Quest 1 Specifications
- **Frame Rate**: 72 FPS (constant)
- **Resolution**: 1440x1600 per eye
- **Latency**: < 20ms (local) / < 50ms (Tailscale)
- **Model Complexity**: < 100k triangles

### Network Requirements
- **Bandwidth**: 10-20 Mbps minimum
- **Ping**: < 50ms
- **WiFi**: 5GHz (802.11ac)
- **Range**: < 10m from router

---

## Changelog

### Version 1.0 (2026-02-04)
- Initial release
- COD-style shooting range interface
- Wireless WiFi and Tailscale support
- Auto-optimization and monitoring
- Complete documentation
- Management scripts
- API endpoints
- Performance tracking

---

## Credits

**Trinity System v2.0**
- Platform: Oculus Quest 1
- Framework: A-Frame 1.5.0 + WebXR
- Server: Python 3 + Custom HTTP handlers
- Network: Tailscale VPN + WiFi
- Design: COD-inspired tactical interface

---

## License

Trinity System - Internal Tool
For personal/educational use only.

---

**Last Updated**: February 4, 2026
**Version**: 1.0
**Status**: Production Ready

**Ready to use!** Start with `./AUTO_DEPLOY_VR.sh`
