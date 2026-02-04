# Trinity Command Center - Setup Guide

## 🎯 Overview

Trinity Command Center unifies three AI-powered systems into one interface:
- **Career Station** 🎯 - Job hunting automation
- **Engineering Station** 🔧 - CAD generation with OpenSCAD
- **Trading Station** 📊 - Bot monitoring and performance

Access from: Desktop, iPhone via Tailscale, or Oculus Quest 1 VR browser.

---

## 📦 Installation

### Step 1: Install Dependencies

```bash
# Navigate to Trinity directory
cd ~/Desktop/Trinity-System

# Install Python packages
pip3 install -r requirements_command_center.txt

# Install OpenSCAD (for CAD generation)
brew install --cask openscad

# Verify installation
streamlit --version
openscad --version
```

### Step 2: Make Launch Script Executable

```bash
chmod +x launch_command_center.sh
```

---

## 🚀 Launch Options

### Option A: Standalone Mode (Recommended for Testing)

Runs Command Center independently on port 8502:

```bash
./launch_command_center.sh
```

Access at:
- Desktop: http://localhost:8502
- iPhone: http://[MAC-MINI-TAILSCALE-IP]:8502
- Quest 1: http://[MAC-MINI-TAILSCALE-IP]:8502

### Option B: Integrated Mode (Production)

Integrates with existing Trinity FastAPI server on port 8001:

**Method 1: Update main.py**

Add to your existing `main.py`:

```python
from trinity_command_mount import mount_command_center

# ... existing code ...

# Mount command center
mount_command_center(app)

# Now start server as usual
```

**Method 2: Run Integration Script**

```bash
python3 trinity_command_mount.py
```

Access at:
- Desktop: http://localhost:8001/command
- iPhone: http://[MAC-MINI-TAILSCALE-IP]:8001/command
- Quest 1: http://[MAC-MINI-TAILSCALE-IP]:8001/command (auto-enables VR mode)

---

## 📱 Device-Specific Setup

### iPhone 17 Setup

1. Ensure Tailscale is running on both iPhone and Mac Mini
2. Get Mac Mini's Tailscale IP:
   ```bash
   tailscale ip -4
   ```
3. On iPhone, open Safari and go to:
   ```
   http://[TAILSCALE-IP]:8001/command
   ```
4. Tap Share → Add to Home Screen
5. Name it "Trinity Command"
6. Now it launches like a native app!

### Oculus Quest 1 Setup

1. Put on Quest headset
2. Open Oculus Browser
3. Navigate to:
   ```
   http://[MAC-MINI-TAILSCALE-IP]:8001/command
   ```
4. System auto-detects Quest and enables VR mode:
   - Larger fonts and buttons
   - Simplified 3D models (<5K triangles)
   - Preview images instead of live 3D renders
5. Bookmark the page for quick access

**VR Mode Features:**
- 🥽 Optimized for Quest 1 hardware
- 🔋 Reduced update frequency to save battery
- 📐 Simplified CAD models for smooth rendering
- 📊 Clear, readable metrics

---

## 🎨 Module Guide

### 🎯 Career Station

**Features:**
- Submit job URLs for AI analysis
- View fit scores and auto-generated cover letters
- Track applications (Pending → Applied → Denied)
- Quick link to full dashboard

**Usage:**
1. Paste job URL into prompt box
2. Click "Analyze Job"
3. Trinity evaluates fit and generates cover letter
4. Review draft and apply manually

### 🔧 Engineering Station

**Features:**
- AI-powered CAD generation using OpenSCAD
- Text-to-3D model pipeline
- Download STL files for 3D printing
- VR optimization for Quest viewing

**Example Prompts:**
- "Design a hex bolt M8x20mm"
- "Create a cable clip for 1/4 inch cables"
- "Make a phone stand with 45 degree angle"
- "Design a door stop wedge"

**Workflow:**
1. Describe what you want in natural language
2. Trinity generates OpenSCAD code
3. Code compiles to STL file automatically
4. Download STL or view in 3D software

**VR Mode:**
- Models automatically simplified to <5K triangles
- PNG previews generated for Quest browser
- Faster render times

### 📊 Trading Station

**Features:**
- Real-time bot status monitoring
- Phoenix (Mark XII) - Options trading
- Genesis (Mark XI) - Equity trading
- Macro status alerts
- Live performance metrics

**Metrics Displayed:**
- Bot online/offline status
- Current positions
- Latest prices and indicators
- Recent trade history
- Log file access

---

## 🛠️ Configuration

### Environment Variables

Required in `.env`:

```bash
# AI APIs (Career + Engineering)
GOOGLE_API_KEY=your_gemini_key
ANTHROPIC_API_KEY=your_claude_key

# Trinity API
TRINITY_API_BASE=http://localhost:8001

# Paths (auto-configured, override if needed)
# BOT_FACTORY_DIR=~/Desktop/Bot-Factory
```

### VR Mode Toggle

Three ways to enable VR mode:

1. **Auto-detect**: Quest browser auto-enables
2. **URL parameter**: Add `?vr=true` to any URL
3. **UI toggle**: Click "VR Mode" in sidebar

### File Storage

```
Trinity-System/
├── email_drafts/           # Job cover letters
├── cad_output/             # CAD models
│   ├── *.scad             # OpenSCAD source code
│   ├── *.stl              # Compiled 3D models
│   └── previews/          # PNG previews
└── job_status.db          # Job tracking database
```

**Cleanup:**
- CAD files older than 30 days: auto-archived (future feature)
- Manual cleanup: `rm -rf cad_output/*.{scad,stl}`

---

## 🔧 Troubleshooting

### Issue: Streamlit won't start

```bash
# Check if port is in use
lsof -i :8502

# Kill conflicting process
kill $(lsof -t -i:8502)

# Restart
./launch_command_center.sh
```

### Issue: OpenSCAD compilation fails

**Symptoms:** "OpenSCAD not installed" error

**Solution:**
```bash
# Install OpenSCAD
brew install --cask openscad

# Verify installation
which openscad

# Should output: /Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD
```

### Issue: Trading bot logs not showing

**Cause:** Bot-Factory directory not found

**Solution:**
1. Check path in command_center.py:
   ```python
   BOT_FACTORY_DIR = BASE_DIR.parent / "Bot-Factory"
   ```
2. Verify bots are running:
   ```bash
   ps aux | grep -E "phoenix|genesis"
   ```

### Issue: VR mode not activating on Quest

**Solutions:**
1. Manually add `?vr=true` to URL
2. Use sidebar toggle: "🥽 VR Mode"
3. Check User-Agent detection in browser (may not contain "Oculus")

### Issue: Job submission fails

**Cause:** Trinity API not running

**Solution:**
```bash
# Check Trinity API status
curl http://localhost:8001/health

# Start Trinity API
cd ~/Desktop/Trinity-System
python3 main.py
```

---

## 🎯 Best Practices

### For Job Hunting:
1. Submit jobs during business hours for best AI performance
2. Review cover letters before applying (Trinity writes well, but you know the job best)
3. Use "Pending → Applied" workflow to track progress
4. Check dashboard daily for new opportunities

### For CAD Generation:
1. Start with simple prompts to test OpenSCAD syntax
2. Use VR mode for Quest viewing (models are optimized)
3. Download STLs immediately (auto-cleanup coming soon)
4. Iterate on designs by modifying the .scad file directly

### For Trading Monitoring:
1. Check status 2-3 times daily (not obsessively)
2. Phoenix = Options (more frequent updates)
3. Genesis = Equities (slower, longer-term)
4. Trust the bots - they use tested strategies

---

## 🚀 Advanced Usage

### Custom Themes

Edit `launch_command_center.sh` to customize:

```bash
--theme.primaryColor="#00FF00"      # Accent color
--theme.backgroundColor="#0E1117"   # Background
--theme.secondaryBackgroundColor="#262730"  # Cards
--theme.textColor="#FAFAFA"         # Text
```

### API Integration

Call modules programmatically:

```python
import requests

# Submit job
response = requests.post("http://localhost:8001/api/submit-job", json={
    "url": "https://company.com/job"
})

# Generate CAD model
response = requests.post("http://localhost:8502/api/generate-cad", json={
    "prompt": "Design a hex bolt M8x20mm",
    "vr_optimize": True
})
```

### Multiple Devices

Run Command Center on multiple devices simultaneously:
- Mac Mini: Full desktop experience
- iPhone: Mobile command center
- Quest 1: VR visualization
- iPad: Tablet interface

All sync via Trinity API backend.

---

## 📊 System Requirements

### Mac Mini (Server)
- macOS Sonoma 14.0+
- Python 3.10+
- 8GB RAM minimum
- 50GB free disk space (for CAD files)

### iPhone 17
- iOS 17+
- Tailscale app installed
- Safari or any modern browser

### Oculus Quest 1
- Firmware 30.0+
- Oculus Browser
- Tailscale sideloaded (or same network as Mac Mini)

---

## 🎬 Quick Start Checklist

- [ ] Install dependencies: `pip3 install -r requirements_command_center.txt`
- [ ] Install OpenSCAD: `brew install --cask openscad`
- [ ] Make script executable: `chmod +x launch_command_center.sh`
- [ ] Get Tailscale IP: `tailscale ip -4`
- [ ] Launch Command Center: `./launch_command_center.sh`
- [ ] Test on desktop: http://localhost:8502
- [ ] Bookmark on iPhone: http://[TAILSCALE-IP]:8502
- [ ] Bookmark on Quest: http://[TAILSCALE-IP]:8502
- [ ] Toggle VR mode and test
- [ ] Submit test job
- [ ] Generate test CAD model
- [ ] Check trading bot status

---

## 🆘 Support

If you encounter issues:

1. Check logs:
   ```bash
   # Streamlit logs
   tail -f ~/.streamlit/logs/*

   # Trinity logs
   tail -f trinity.log
   ```

2. Verify services:
   ```bash
   # Trinity API
   curl http://localhost:8001/health

   # Command Center
   curl http://localhost:8502/_stcore/health
   ```

3. Restart everything:
   ```bash
   # Kill all Trinity processes
   pkill -f "trinity\|streamlit\|command_center"

   # Restart
   ./launch_command_center.sh
   ```

---

**Ready to launch!** 🚀

Run: `./launch_command_center.sh`

Access: http://localhost:8502
