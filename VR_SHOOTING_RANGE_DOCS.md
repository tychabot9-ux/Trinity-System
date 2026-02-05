# Trinity VR Tactical Engineering Workspace
## COD-Style Shooting Range Interface Documentation

### Overview
The Trinity VR Workspace features a Call of Duty-inspired shooting range interface designed for intuitive 3D CAD model manipulation in VR using the Oculus Quest 1.

---

## Interface Components

### 1. Shooting Range Targets (Tool Selection)
Located 8 meters in front of the user, these are the primary tool selection mechanism.

#### Target Layout
```
   [ROTATE]    [SCALE]    [MOVE]
      ↻          ⊕          ⇄
   Target 1   Target 2   Target 3
```

#### Target Design
- **Outer Ring**: Black (#111) - Radius 0.8-1.0m
- **Middle Ring**: Green (#0f0) - Radius 0.6-0.8m (70% opacity)
- **Inner Ring**: Black (#111) - Radius 0.4-0.6m
- **Bullseye**: Light Green (#0c0) - Radius 0.4m
- **Label**: Tool name in green (#0f0)
- **Icon**: Bold black icon on bullseye

#### Interaction
- **Aim**: Point controller laser at target
- **Fire**: Pull trigger to select tool
- **Feedback**: Target pulses and scales up (1.2x) on hit
- **Sound**: "Shoot" sound effect plays
- **Visual**: Bullseye flashes white briefly

---

### 2. Radial Menu (COD Weapon Wheel Style)
Appears 0.5m in front of user when summoned.

#### Menu Items (8 positions)
```
       [GEN]
   [HOME] ⊕ [LOAD]
[TOOL]       [SAVE]
   [SET]   [DEL]
     [EXP]
```

| Position | Action | Color | Description |
|----------|--------|-------|-------------|
| North | GENERATE | Green | Generate new CAD model via AI |
| NE | LOAD | Green | Load existing model |
| East | SAVE | Green | Save current model |
| SE | DELETE | Red | Delete current model |
| South | EXPORT | Green | Export model to file |
| SW | SETTINGS | Blue | Open settings menu |
| West | TOOLS | Green | Tool submenu |
| NW | HOME | Green | Return to home position |

#### Controls
- **Open Menu**: Y Button (left) or B Button (right)
- **Select**: Point and trigger
- **Close**: Y/B Button again

---

### 3. Model Display Stage
Central holographic pedestal for displaying 3D models.

#### Features
- **Tactical Display Pedestal**
  - Green metallic cylinder (radius: 0.6m, height: 0.1m)
  - Emissive glow effect
  - Black inner platform

- **Holographic Grid Base**
  - Wireframe plane (1.2m x 1.2m)
  - Green (#0f0) with 40% opacity
  - Rotates continuously (360° in 20 seconds)

- **Model Container**
  - Auto-scales models to fit (0.1x default)
  - Applies rotation animation
  - Positioned 0.2m above pedestal

---

### 4. COD-Style HUD (Heads-Up Display)

#### Top Right - Status Display
```
TRINITY TACTICAL
TOOL: ROTATE
STATUS: READY
```
- Font: Orbitron (green)
- Position: 0.3m right, 0.2m up, 0.5m forward
- Updates in real-time

#### Bottom Right - Model Counter (Ammo Style)
```
MODELS: 3
```
- Large bold font
- Tracks number of loaded models
- Mimics COD ammo counter

#### Bottom Left - Minimap
```
┌─────────┐
│   MAP   │
│    •    │ ← Player position
└─────────┘
```
- 0.15m x 0.15m square
- Black background with green border
- Shows player position as green dot

#### Center - Crosshair
- Two-ring reticle system
- Outer ring: 0.01-0.012m radius
- Center dot: 0.002m radius
- Green (#0f0), 80% opacity
- Always 1m from camera

---

### 5. Controller Layout

#### Left Controller (Menu/Tool Selection)
```
    [Y] Toggle Menu
    [X] Quick Tool Cycle
   [Grip] Grab Object
[Thumbstick] Movement
 [Trigger] Shoot/Select
```

#### Right Controller (Primary Interaction)
```
    [B] Toggle Menu
    [A] Quick Action
   [Grip] Grab Object
[Thumbstick] Movement
 [Trigger] Shoot/Select
```

---

## Control Schemes

### Basic Navigation
- **Movement**: Left thumbstick (forward/back/strafe)
- **Turning**: Right thumbstick (snap turn)
- **Height**: Physical movement (room-scale)

### Tool Selection Methods

#### Method 1: Shooting Range (Primary)
1. Point controller at desired target
2. Pull trigger to "shoot" and select tool
3. Confirmation via HUD update

#### Method 2: Quick Cycle
1. Press X (left) or A (right) button
2. Cycles through: ROTATE → SCALE → MOVE
3. Instant tool change

#### Method 3: Radial Menu
1. Press Y (left) or B (right) to open menu
2. Point at TOOLS section
3. Select from expanded tool list

---

### Model Manipulation

#### Rotate Tool
- **Grip**: Hold grip while moving controller
- **Precision**: Slow controller movement = fine rotation
- **Axes**: X/Y/Z rotation based on controller orientation

#### Scale Tool
- **Grip**: Hold grip, move controllers apart/together
- **Uniform**: Both controllers = uniform scaling
- **Axis**: Single controller = axis-based scaling

#### Move Tool
- **Grip**: Hold grip, move controller
- **Lock Axis**: Hold A/X while moving for axis lock
- **Precision**: Thumbstick press = precision mode

---

## Environment Features

### 1. Tactical Grid Floor
- 100m x 100m wireframe grid
- Green (#0f0) lines, 30% opacity
- Provides spatial reference
- Flat shader for performance

### 2. Room Boundary Guardian
Dynamic visualization based on room scan:
- Green wireframe walls
- 2m height
- 30% opacity
- Prevents walking into walls
- Auto-generated from Guardian API

### 3. Tron-Style Environment
- Preset: "tron" theme
- Ground: Black (#0a0a0a)
- Grid: Cross pattern, green
- Horizon: Dark green (#001100)
- Fog: 50% density

### 4. Tactical Lighting
- **Ambient**: 30% intensity, green tint
- **Directional 1**: 60% intensity, position (5, 10, 5)
- **Directional 2**: 40% intensity, position (-5, 10, -5)
- **Point**: 50% intensity, overhead (0, 3, 0)

---

## Performance Optimization

### Auto-Optimization System
Monitors and adjusts quality every 5 seconds:

```javascript
setInterval(() => {
    const fps = scene.stats.fps;
    if (fps < 60) {
        // Reduce render quality
        // Simplify models
        // Disable effects
    }
}, 5000);
```

### Wireless Optimization Settings
- **Renderer**: Anti-aliasing enabled
- **Color Management**: Enabled
- **Sort Objects**: True (depth sorting)
- **Physically Correct Lights**: True
- **High Refresh Rate**: Enabled for Quest 1 (72Hz)

### Network Monitoring
Checks connection every 10 seconds:
- Tests `/api/status` endpoint
- Updates HUD on connection loss
- Auto-reconnect on restore

---

## API Integration

### Available Endpoints

#### GET /api/models
Returns list of available CAD models:
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

#### POST /api/generate_cad
Generate new CAD model via AI:
```json
// Request
{
  "prompt": "tactical hex bolt M8"
}

// Response
{
  "status": "success",
  "filename": "test_bolt.stl",
  "message": "Generating: tactical hex bolt M8",
  "timestamp": "2026-02-04T12:00:00"
}
```

#### GET /api/status
Server health and network info:
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
    "local": "192.168.1.248"
  }
}
```

---

## Sound Effects

### Select Sound
- Triggered on: Menu interactions, tool changes
- Type: Soft beep
- Volume: Medium

### Shoot Sound
- Triggered on: Target hits
- Type: Tactical weapon fire (suppressed)
- Volume: Medium-high

### Implementation
Uses embedded base64 WAV data for instant loading.

---

## Visual Feedback System

### Target Hit Effects
1. **Scale Animation**: Target scales to 1.2x for 200ms
2. **Color Flash**: Bullseye flashes white
3. **Sound**: Shoot sound plays
4. **HUD Update**: Status text changes

### Menu Selection
1. **Highlight**: Selected item brightens
2. **Sound**: Selection beep
3. **HUD Update**: Action name displayed

### Tool Activation
1. **Visual**: Tool icon pulses
2. **HUD**: "TOOL: [NAME]" update
3. **Controller**: Haptic feedback (if supported)

---

## Troubleshooting Guide

### Common Issues

#### 1. Controllers Not Appearing
- **Cause**: Oculus controllers not detected
- **Fix**: Ensure Quest controllers are on and paired
- **Alternative**: Use desktop pointer mode

#### 2. Targets Not Responding
- **Cause**: Raycaster not configured
- **Fix**: Check controller raycaster settings
- **Debug**: Enable laser visibility (green line)

#### 3. Models Not Loading
- **Cause**: CAD files not in correct directory
- **Fix**: Verify files in `/cad_output/` directory
- **Format**: Ensure files are `.stl` or `.gltf`

#### 4. Low Frame Rate
- **Cause**: Complex models or poor wireless signal
- **Fix**: Auto-optimization will adjust quality
- **Manual**: Reduce model complexity or move closer to router

#### 5. Network Disconnection
- **Symptom**: "CONNECTION LOST" in HUD
- **Fix**: Check WiFi signal strength
- **Alternative**: Use Tailscale VPN connection

---

## Advanced Features

### Custom Target Creation
Add custom tool targets to shooting range:

```javascript
<a-entity class="target" data-tool="custom" position="4 0 0">
    <a-ring radius-inner="0.8" radius-outer="1" color="#111"></a-ring>
    <a-circle radius="0.4" color="#0c0"></a-circle>
    <a-text value="CUSTOM" align="center" color="#0f0"></a-text>
</a-entity>
```

### Custom Menu Actions
Add items to radial menu:

```javascript
<a-entity class="menu-item" data-action="custom" position="0 0.01 -0.3">
    <a-box width="0.15" height="0.02" depth="0.15" color="#0f0"></a-box>
    <a-text value="CUSTOM" align="center" color="#000"></a-text>
</a-entity>
```

### Controller Event Handling
Register custom controller events:

```javascript
el.addEventListener('triggerdown', () => {
    // Custom trigger action
});

el.addEventListener('gripdown', () => {
    // Custom grip action
});
```

---

## Performance Benchmarks

### Target Specifications (Quest 1)
- **Frame Rate**: 72 FPS constant
- **Resolution**: 1440x1600 per eye
- **Latency**: < 20ms total (network + render)
- **Model Complexity**: < 100k triangles recommended

### Network Requirements
- **Bandwidth**: 5-10 Mbps minimum
- **Latency**: < 50ms ping time
- **Connection**: WiFi 5 (802.11ac) or better
- **Range**: < 10 meters from router

---

## Best Practices

### 1. Room Setup
- Clear 2m x 2m space minimum
- Good lighting for tracking
- Set up Guardian boundary
- Position router for optimal signal

### 2. Model Optimization
- Keep triangle count under 100k
- Use simple materials
- Enable LOD (Level of Detail)
- Compress textures

### 3. Wireless Optimization
- 5GHz WiFi band preferred
- Dedicated VR network if possible
- Router within line of sight
- Minimize network traffic

### 4. User Comfort
- Take breaks every 30 minutes
- Adjust IPD (Inter-Pupillary Distance)
- Calibrate floor height
- Use comfort settings if needed

---

## Future Enhancements

### Planned Features
- [ ] Voice commands for tool selection
- [ ] Gesture-based model manipulation
- [ ] Multi-user collaborative mode
- [ ] Haptic feedback for collisions
- [ ] Advanced CAD editing tools
- [ ] Real-time Trinity AI integration
- [ ] Model version control
- [ ] Export to multiple formats
- [ ] Custom shooting range layouts
- [ ] Achievement system

---

## Credits

**Trinity System v2.0**
- VR Interface: COD-inspired tactical design
- Framework: A-Frame 1.5.0 + aframe-extras
- Hardware: Oculus Quest 1
- Network: Tailscale VPN + Local WiFi
- Server: Python 3 + Custom HTTP handlers

**Design Philosophy**
Combining the intuitive, engaging mechanics of Call of Duty's weapon selection with professional CAD engineering tools to create an immersive, productive VR workspace.

---

## Support

For issues, improvements, or questions:
- Check logs: `/Users/tybrown/Desktop/Trinity-System/logs/`
- Server status: `http://[IP]:8503/api/status`
- Restart server: `./restart_vr_server.sh restart`

**Last Updated**: February 4, 2026
**Version**: 1.0
**Status**: Production Ready
