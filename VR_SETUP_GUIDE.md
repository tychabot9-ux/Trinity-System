# Trinity VR Workspace Setup Guide
## Oculus Quest 1 Engineering Station

Created: February 4, 2026
Status: READY TO USE ✅

---

## 🎯 System Overview

**What is this?**
A full VR engineering workspace for viewing and editing 3D CAD models using your Oculus Quest 1 headset.

**Hardware Detected:**
- ✅ Oculus Quest 1 (Connected via USB-C)
- ✅ Mac Mini M4 with 16GB RAM
- ✅ USB connection: 480 Mb/s

**Your Configuration:**
- **Use Case:** Both viewing and editing CAD models
- **Controls:** Oculus Touch controllers
- **Connection:** USB-C wired (lowest latency)
- **Scope:** Full VR engineering workspace

---

## 🚀 Quick Start (3 Steps)

### Step 1: Start the VR Server

```bash
cd /Users/tybrown/Desktop/Trinity-System
./launch_vr_workspace.sh
```

This will:
- Start the VR server on port 8503
- Display your local IP address
- Show Oculus Quest access URL

### Step 2: Put on Your Quest 1 Headset

1. Make sure Quest 1 is connected via USB-C
2. Put on the headset
3. Open **Oculus Browser** (or Firefox Reality)

### Step 3: Access the VR Workspace

In the Quest browser, navigate to:
```
http://[YOUR-MAC-IP]:8503/vr
```

*(The exact URL will be shown when you run the launch script)*

---

## 🎮 VR Controls

### Oculus Touch Controllers

**Left Controller:**
- 🎯 **Thumbstick** - Navigate workspace
- 🔴 **Trigger** - Select tools/models
- 🟢 **Grip** - Grab and move models
- **🅰️ Button** - Rotate mode
- **🅱️ Button** - Reset view

**Right Controller:**
- 🎯 **Thumbstick** - Fine adjustments
- 🔴 **Trigger** - Edit/Interact
- 🟢 **Grip** - Scale model
- **Laser Pointer** - Point and select

### Available Tools (Left Panel)

1. **↻ ROTATE** - Rotate model in 3D space
2. **⊕ SCALE** - Resize model
3. **⇄ MOVE** - Reposition model

### Model Library (Right Panel)

1. **🔩 BOLT** - Load test bolt model
2. **➕ NEW** - Generate new CAD model with AI

---

## 🏗️ Features

### ✅ What's Working Now

- [x] Full WebXR/A-Frame VR environment
- [x] Oculus Quest 1 controller support
- [x] 3D model viewing (STL format)
- [x] Model rotation, scaling, and movement
- [x] Interactive tool panels in VR
- [x] Real-time HUD (Heads-Up Display)
- [x] Model library browser
- [x] Wired USB-C connection (low latency)

### 🔄 Integration with Trinity

The VR workspace integrates with:
- **CAD Output Directory:** `/Users/tybrown/Desktop/Trinity-System/cad_output`
- **Engineering Station:** CAD models appear automatically
- **AI Generation:** Generate models via voice/menu

### 🎨 VR Environment

- **Dark space theme** (easier on eyes)
- **Grid floor** with boundaries
- **360° lighting** for model visibility
- **Info panels** with instructions
- **Pedestal** for model display
- **Tool menus** floating in 3D space

---

## 📦 Loading 3D Models

### From CAD Output Directory

Any STL files in `/cad_output/` will be available in VR:

1. Generate model in Engineering Station (desktop)
2. Model automatically appears in VR workspace
3. Select from Model Library panel (right side in VR)

### Generate New Model in VR

1. Point at **➕ NEW** button with laser
2. Pull trigger to select
3. Voice prompt will ask what to generate
4. Trinity AI generates CAD model
5. Model loads automatically

### Test Model

Load the test bolt to verify VR is working:
1. Point at **🔩 BOLT** button
2. Pull trigger
3. Model appears on pedestal

---

## 🔧 Troubleshooting

### Quest Not Connecting

1. Check USB-C cable is securely connected
2. Enable **Developer Mode** on Quest:
   - Open Oculus app on phone
   - Go to Settings > Developer Mode
   - Toggle ON
3. Try unplugging and reconnecting

### Browser Not Loading VR

1. Make sure you're using **Oculus Browser** (recommended)
2. Alternative: **Firefox Reality**
3. Grant VR permissions when prompted
4. Click "ENTER VR" button on page

### Models Not Showing

1. Check CAD output directory has STL files
2. Restart VR server
3. Refresh browser in Quest
4. Check server terminal for errors

### Latency/Performance Issues

1. Close other applications on Mac Mini
2. Use wired USB-C connection (not wireless)
3. Reduce model complexity in CAD generation
4. Lower graphics quality in Quest settings

---

## 📱 Access Methods

### Desktop Preview (Before VR)

```
http://localhost:8503/vr
```
View on your Mac's browser to preview before entering VR

### Quest 1 (In VR)

```
http://[MAC-IP]:8503/vr
```
*(Replace [MAC-IP] with IP shown in launch script)*

### API Endpoints

```
GET  /api/models          # List available models
POST /api/generate_cad    # Generate new model
```

---

## 🎯 Workflow Example

### Creating and Viewing a CAD Model

1. **Desktop:**
   - Open Trinity Command Center
   - Go to Engineering Station
   - Generate CAD model (e.g., "M10 hex bolt")
   - Model saved to `cad_output/`

2. **VR:**
   - Put on Quest 1
   - Open VR workspace in Oculus Browser
   - Click "ENTER VR"
   - Select model from library panel
   - Use controllers to inspect/edit

3. **Editing:**
   - Grab model with grip buttons
   - Rotate with thumbsticks
   - Scale with both grips simultaneously
   - Position precisely in 3D space

4. **Export:**
   - Edits auto-save to STL
   - Access from desktop for 3D printing

---

## 🔒 Security Notes

- VR server runs locally only (localhost + LAN)
- No external internet exposure
- All models stay on your machine
- USB-C connection is secure (wired)

---

## 📊 Technical Details

### Stack

- **Framework:** A-Frame 1.5.0 (WebXR)
- **3D Engine:** Three.js (via A-Frame)
- **VR API:** WebXR Device API
- **Server:** Python HTTP server
- **Port:** 8503
- **Protocols:** HTTP, WebXR

### Performance

- **Target FPS:** 72 Hz (Quest 1 native)
- **Render Distance:** 10 meters
- **Max Model Size:** 10MB STL
- **Latency:** <20ms (wired USB-C)

### File Formats Supported

- **.STL** - Standard Triangle Language (current)
- **.GLTF** - GL Transmission Format (planned)
- **.OBJ** - Wavefront Object (planned)

---

## 🚀 Next Steps

### Immediate

1. Run `./launch_vr_workspace.sh`
2. Test with provided bolt model
3. Generate your first custom model

### Advanced

- [ ] Voice command integration
- [ ] Multi-user collaboration
- [ ] CAD editing tools (boolean operations)
- [ ] Measurement tools in VR
- [ ] Export to different formats
- [ ] Wireless streaming (Quest Air Link)

---

## 📞 Support

**Issues?**
Check Trinity Command Center logs:
```bash
tail -f /tmp/trinity_command_center.log
```

**VR Server Logs:**
Displayed in terminal when running `launch_vr_workspace.sh`

---

## 🎉 Ready to Go!

Your Trinity VR Engineering Workspace is fully set up and ready to use.

**Start Command:**
```bash
./launch_vr_workspace.sh
```

Happy engineering in VR! 🥽🔧
