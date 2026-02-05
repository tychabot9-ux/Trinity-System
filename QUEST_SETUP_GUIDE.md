# Oculus Quest 1 Setup Guide
## Trinity VR Tactical Engineering Workspace

### Quick Start Guide

---

## Prerequisites

### Hardware Requirements
- Oculus Quest 1 (64GB or 128GB)
- WiFi network (5GHz recommended)
- Mac/PC running Trinity VR Server
- USB-C cable (for initial setup/charging)

### Software Requirements
- Quest firmware: Latest version
- Browser: Oculus Browser (pre-installed)
- Optional: SideQuest for advanced features

---

## Network Setup

### Option 1: Local WiFi (Recommended for lowest latency)

**Connection URL**:
```
http://192.168.1.216:8503/vr
```

**Setup Steps**:
1. Ensure Quest and Mac are on same WiFi network
2. Open Oculus Browser on Quest
3. Navigate to URL above
4. Bookmark for quick access

**Advantages**:
- Lowest latency (< 20ms)
- No external dependencies
- Maximum bandwidth
- Works offline

### Option 2: Tailscale VPN (Recommended for remote access)

**Connection URL**:
```
http://100.66.103.8:8503/vr
```

**Setup Steps**:
1. Install Tailscale app on Quest (via SideQuest)
2. Log in to your Tailscale account
3. Open Oculus Browser
4. Navigate to URL above
5. Bookmark for quick access

**Advantages**:
- Access from anywhere
- Secure encrypted connection
- Works across networks
- Great for remote work

---

## Step-by-Step Setup

### 1. Initial Quest Setup

#### First Time Setup
1. **Power On**: Hold power button for 2 seconds
2. **Language**: Select your language
3. **WiFi**: Connect to your network
4. **Account**: Log in to Facebook/Meta account
5. **Guardian**: Set up play area boundary
6. **Controllers**: Pair Oculus Touch controllers

#### Guardian Boundary Setup
1. Put on headset
2. Follow on-screen instructions
3. Draw boundary with controller
4. Minimum 2m x 2m recommended
5. Mark any obstacles

### 2. Network Configuration

#### Check Your IP Address
On your Mac, run:
```bash
cd /Users/tybrown/Desktop/Trinity-System
./AUTO_DEPLOY_VR.sh
```

This will display:
- Local WiFi IP
- Tailscale IP
- Access URLs

#### Test Connection
1. Open Oculus Browser on Quest
2. Navigate to `http://[IP]:8503/api/status`
3. Should see JSON status response
4. If successful, proceed to VR URL

### 3. Launch VR Workspace

#### Using Oculus Browser
1. **Open Browser**:
   - Press Oculus button on right controller
   - Select "Browser" from menu

2. **Navigate to Trinity**:
   - Type URL: `http://192.168.1.216:8503/vr`
   - Or use bookmarked link

3. **Load Workspace**:
   - Wait for loading screen (green theme)
   - Watch progress bar
   - Click "DEPLOY TO VR" button

4. **Enter VR Mode**:
   - Browser will request VR permission
   - Click "Allow" or "Enter VR"
   - Put on headset if not already wearing

---

## QR Code Setup (Quick Access)

### Generate QR Code

You can generate a QR code for quick access. Use this URL:
```
http://192.168.1.216:8503/vr
```

#### Online QR Code Generator
1. Go to: https://www.qr-code-generator.com/
2. Select "URL" type
3. Enter: `http://192.168.1.216:8503/vr`
4. Download QR code image
5. Print or display on screen

#### Using Python (Included Script)
```bash
cd /Users/tybrown/Desktop/Trinity-System
python3 generate_qr_code.py
```

This creates: `trinity_vr_qr.png`

#### Scan QR Code on Quest
1. Open Camera app on Quest (if available)
2. Or use phone to scan and send link
3. Open link in Oculus Browser

---

## Controller Setup

### Oculus Touch Controllers

#### Battery Installation
1. Slide off battery cover (bottom of handle)
2. Insert AA battery (included with Quest)
3. Replace cover
4. Repeat for second controller

#### Pairing Controllers
1. Turn on controllers (automatically pair on first use)
2. If not paired:
   - Hold Oculus + B (right controller)
   - Hold Oculus + Y (left controller)
3. Follow on-screen pairing instructions

#### Controller Orientation
- **Left Controller**: Menu/tool selection
- **Right Controller**: Primary interaction
- Both have identical button layouts

### Button Layout Reference

```
        [Y/B]           Top Button (Menu)
        [X/A]           Bottom Button (Quick Action)
         | |
    _____|_|_____
   |             |
   |   [○]       |      Thumbstick
   |             |
   |_____________|
         | |             Grip (sides)
         |_|             Trigger (front)
```

---

## Trinity Interface Tutorial

### First Launch Walkthrough

#### Step 1: Loading Screen
- Green tactical theme loads
- Progress bar shows initialization
- Network status displayed
- "DEPLOY TO VR" button appears

#### Step 2: Initial View
- You'll see tactical grid floor
- Shooting range targets ahead (8m away)
- Room boundary (green wireframe)
- HUD elements in view
- Controllers visible as green lasers

#### Step 3: Basic Movement
- **Walk**: Physical movement in play space
- **Teleport**: Left thumbstick forward + release
- **Rotate**: Right thumbstick left/right
- **Height**: Duck/jump physically

### Selecting Your First Tool

#### Method 1: Shoot a Target (Recommended)
1. Point right controller at center target (SCALE)
2. Align crosshair with bullseye
3. Pull trigger
4. Target will pulse and flash
5. HUD updates to show "TOOL: SCALE"

#### Method 2: Quick Cycle
1. Press X (left) or A (right) button
2. Tool cycles: ROTATE → SCALE → MOVE
3. Watch HUD for current tool

### Using the Radial Menu

1. **Open Menu**: Press Y (left) or B (right)
2. **Navigate**: Point controller at menu items
3. **Select**: Pull trigger on highlighted item
4. **Close**: Press Y/B again

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Can't Connect to Server
**Symptoms**: Page won't load, connection timeout

**Solutions**:
- Verify server is running on Mac
- Check both devices on same WiFi network
- Ping server: `http://[IP]:8503/api/status`
- Restart server: `./restart_vr_server.sh restart`
- Check firewall settings on Mac

#### Issue 2: Controllers Not Showing
**Symptoms**: No laser pointers, can't interact

**Solutions**:
- Ensure controllers have fresh batteries
- Re-pair controllers (Oculus + B/Y)
- Restart Quest
- Check controller tracking in Settings

#### Issue 3: Choppy/Laggy Performance
**Symptoms**: Low frame rate, stuttering

**Solutions**:
- Move closer to WiFi router
- Switch to 5GHz WiFi band
- Reduce model complexity
- Close other apps on Quest
- Check network bandwidth usage

#### Issue 4: Tracking Lost
**Symptoms**: View drifts, controllers jump

**Solutions**:
- Improve room lighting
- Remove reflective surfaces
- Clean Quest cameras (microfiber cloth)
- Redefine Guardian boundary
- Check for IR interference

#### Issue 5: Can't Enter VR Mode
**Symptoms**: "DEPLOY TO VR" button doesn't work

**Solutions**:
- Grant VR permissions to browser
- Ensure browser supports WebXR
- Update Oculus Browser
- Try different browser (Wolvic, Firefox Reality)

---

## Performance Optimization

### Network Optimization

#### WiFi Setup
1. Use 5GHz band (not 2.4GHz)
2. Set router channel to less congested one
3. Enable QoS (Quality of Service) for Quest
4. Disable bandwidth-heavy apps during VR

#### Bandwidth Requirements
- Minimum: 5 Mbps
- Recommended: 10-20 Mbps
- Optimal: 50+ Mbps
- Latency: < 50ms ping

### Quest Settings

#### Graphics Settings
1. Settings → Developer
2. Enable Performance Overlay
3. Monitor FPS (target: 72 FPS)
4. Adjust auto-optimization if needed

#### Power Settings
- Keep Quest plugged in for extended sessions
- Battery life: ~2-3 hours unplugged
- USB-C can provide power while in use

---

## Advanced Features

### Developer Mode (Optional)

#### Enable Developer Mode
1. Open Oculus mobile app
2. Go to Settings → Quest
3. Enable Developer Mode
4. Restart Quest

#### Benefits
- Install custom apps via SideQuest
- Access developer tools
- Advanced performance metrics
- Custom settings

### SideQuest Setup (Optional)

#### Installation
1. Download SideQuest: https://sidequestvr.com/
2. Enable Developer Mode on Quest
3. Connect Quest to PC via USB-C
4. Launch SideQuest
5. Install additional browsers or tools

#### Useful Apps
- Wolvic Browser (alternative browser)
- FPS Monitor
- Advanced Settings
- File Manager

---

## Bookmarks and Quick Access

### Browser Bookmarks

#### Save Trinity Workspace
1. Navigate to Trinity URL
2. Click menu (three dots)
3. Select "Add Bookmark"
4. Name: "Trinity VR"
5. Save to Bookmarks Bar

#### Home Screen Shortcut
1. In Oculus Browser settings
2. Add to Home Screen
3. Creates icon in Quest library

### Voice Commands (Quest 2+)
Not available on Quest 1, but works on newer models:
- "Hey Facebook, open browser"
- Navigate manually to bookmarked site

---

## Safety Guidelines

### VR Safety

#### Before Each Session
- Clear play area of obstacles
- Ensure Guardian boundary is set
- Check controller batteries
- Adjust head strap for comfort

#### During Sessions
- Take 10-minute breaks every 30 minutes
- Stay aware of real-world surroundings
- Don't use near stairs or hazards
- Stop if feeling dizzy or nauseous

#### Comfort Settings
- Adjust IPD slider (between lenses)
- Tighten head straps for stability
- Clean lenses before use
- Room temperature: 60-85°F

### VR Sickness Prevention
- Start with short sessions (15-20 min)
- Gradually increase duration
- Use teleport instead of smooth movement
- Enable comfort vignette if available
- Stop immediately if feeling unwell

---

## Maintenance

### Quest Maintenance

#### Daily
- Wipe lenses with microfiber cloth
- Check battery levels
- Ensure controllers are off when not in use

#### Weekly
- Clean face interface with sanitizing wipe
- Check for firmware updates
- Charge controllers fully

#### Monthly
- Update Oculus software
- Clean all sensors with dry cloth
- Check head strap condition

### Server Maintenance

#### Check Server Status
```bash
cd /Users/tybrown/Desktop/Trinity-System
./restart_vr_server.sh status
```

#### View Logs
```bash
tail -f /Users/tybrown/Desktop/Trinity-System/logs/vr_server.log
```

#### Restart Server
```bash
./restart_vr_server.sh restart
```

---

## Network URLs Reference

### Primary URLs
```
Local WiFi:  http://192.168.1.216:8503/vr
Tailscale:   http://100.66.103.8:8503/vr
Localhost:   http://localhost:8503/vr (Mac only)
```

### API Endpoints
```
Status:      http://192.168.1.216:8503/api/status
Models:      http://192.168.1.216:8503/api/models
Generate:    http://192.168.1.216:8503/api/generate_cad (POST)
```

### Testing
```bash
# Test server status
curl http://192.168.1.216:8503/api/status

# Test from Quest browser
http://192.168.1.216:8503/api/status
```

---

## Quick Reference Card

### Controller Buttons
- **Trigger**: Select/Shoot
- **Grip**: Grab/Manipulate
- **A/X**: Quick action
- **B/Y**: Menu toggle
- **Thumbstick**: Movement
- **Oculus**: System menu

### Tool Selection
1. Point at target
2. Pull trigger
3. Watch HUD confirm

### Menu Access
1. Press B or Y
2. Point at item
3. Pull trigger

### Emergency Exit
- Press Oculus button
- Select "Exit" from menu

---

## Support and Resources

### Troubleshooting Resources
- Trinity Logs: `/Users/tybrown/Desktop/Trinity-System/logs/`
- Server Status: `http://[IP]:8503/api/status`
- Oculus Support: https://support.oculus.com/

### Documentation
- VR Interface Docs: `VR_SHOOTING_RANGE_DOCS.md`
- Server Code: `vr_server.py`
- Wireless Interface: `vr_workspace_wireless.html`

### Commands
```bash
# Start server
./AUTO_DEPLOY_VR.sh

# Restart server
./restart_vr_server.sh restart

# Check status
./restart_vr_server.sh status

# View logs
tail -f logs/vr_server.log
```

---

## Checklist

### Pre-Session Checklist
- [ ] Server running on Mac
- [ ] Quest charged (> 50%)
- [ ] Controllers have fresh batteries
- [ ] WiFi connection stable
- [ ] Play area clear
- [ ] Guardian boundary set
- [ ] Lenses clean

### Post-Session Checklist
- [ ] Exit VR properly
- [ ] Turn off controllers
- [ ] Clean face interface
- [ ] Charge Quest
- [ ] Check for updates
- [ ] Server can stay running

---

**Setup Complete!**

You're now ready to use the Trinity VR Tactical Engineering Workspace on your Oculus Quest 1.

**Quick Start**:
1. Put on Quest
2. Open Browser
3. Go to: `http://192.168.1.216:8503/vr`
4. Click "DEPLOY TO VR"
5. Start creating!

---

**Last Updated**: February 4, 2026
**Version**: 1.0
**Hardware**: Oculus Quest 1
**Status**: Production Ready
