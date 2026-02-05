# Trinity AVA Voice System Setup

## Current Status

**Voice Engine:** pyttsx3 (System Voice)
**Voice Name:** Ava or Samantha (macOS)
**Quality:** High (offline)
**Devices:** Unified across Mac and Quest

---

## Upgrade to Microsoft AVA Neural Voice (Premium)

For the true Microsoft AVA multilingual neural voice with professional Stark-style tone, you need Azure Cognitive Services.

### Step 1: Get Azure Speech Service Credentials

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a **Speech Service** resource
3. Copy your **Key** and **Region**

### Step 2: Configure Trinity

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export AZURE_SPEECH_KEY="your-speech-service-key-here"
export AZURE_SPEECH_REGION="eastus"  # or your region
```

Then reload:
```bash
source ~/.zshrc
```

### Step 3: Restart Trinity Services

```bash
# Restart VR server with voice
pkill -f vr_server.py
python3 vr_server.py &

# Test voice
python3 trinity_voice.py
```

---

## Voice Comparison

| Feature | System Voice (Current) | Azure AVA (Premium) |
|---------|----------------------|---------------------|
| Quality | High | Neural (Best) |
| Offline | ✅ Yes | ❌ No |
| Cost | Free | $1 per 1M chars |
| Voice | Ava/Samantha | AVA Multilingual |
| Styles | Basic | Professional, Newscast, etc |
| Languages | English | 50+ languages |
| Stark-like | Good | Excellent |

---

## Unified Voice Configuration

Trinity automatically uses the same voice across all devices:
- **Mac:** Direct audio output
- **Quest:** Audio via VR server API

The voice system intelligently detects which device is active and routes audio accordingly.

---

## Voice API Endpoints

### Speak Text
```bash
curl -X POST http://localhost:8503/api/speak \
  -H "Content-Type: application/json" \
  -d '{"text":"Trinity systems online"}'
```

### Announce Action
```bash
curl -X POST http://localhost:8503/api/speak \
  -H "Content-Type: application/json" \
  -d '{"action":"vr_connected"}'
```

### From Quest VR (JavaScript)
```javascript
// Announce action
await fetch('/api/speak', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({action: 'cad_generating'})
});

// Custom text
await fetch('/api/speak', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text: 'Model generation complete'})
});
```

---

## Available Actions

Pre-programmed Stark-style announcements:

- `startup` - "Trinity System online. All systems operational."
- `vr_connected` - "VR workspace connected. Engineering mode active."
- `vr_disconnected` - "VR workspace disconnected. Returning to desktop mode."
- `clipboard_sync` - "Clipboard synced."
- `cad_generating` - "Generating CAD model. Stand by."
- `cad_complete` - "CAD generation complete. Model ready for review."
- `trade_executed` - "Trade executed."
- `alert` - "Attention required."
- `error` - "Error detected."
- `command_center` - "Command Center active. All stations ready."
- `optimization` - "Running optimization protocols."
- `shutdown` - "Trinity System shutting down. Goodbye."

---

## Voice Customization

Edit `/Users/tybrown/Desktop/Trinity-System/.trinity_voice_config.json`:

```json
{
  "voice": "en-US-AvaMultilingualNeural",
  "style": "professional",
  "rate": "1.0",
  "pitch": "0%",
  "device": "auto"
}
```

Options:
- **voice:** Voice ID (Azure) or voice name (system)
- **style:** `professional`, `friendly`, `newscast`, `customerservice`
- **rate:** `0.5` (slow) to `2.0` (fast)
- **pitch:** `-50%` (lower) to `+50%` (higher)
- **device:** `auto`, `mac`, or `quest`

---

## Testing

### Test Voice Output
```bash
python3 trinity_voice.py
```

### Test from VR Workspace
1. Open Quest browser: http://192.168.1.216:8503/vr
2. Open console (F12)
3. Run:
```javascript
await fetch('/api/speak', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text: 'Testing voice from Quest'})
});
```

---

## Troubleshooting

**No voice output:**
```bash
# Check voice system
python3 trinity_voice.py

# Check audio devices
system_profiler SPAudioDataType
```

**Azure voice not working:**
```bash
# Verify credentials
echo $AZURE_SPEECH_KEY
echo $AZURE_SPEECH_REGION

# Check Azure quota
# https://portal.azure.com -> Your Speech Resource -> Usage
```

**Quest not hearing voice:**
- Ensure VR server is running
- Check Quest audio settings
- Verify `/api/speak` endpoint responds:
```bash
curl http://192.168.1.216:8503/api/speak -X POST \
  -H "Content-Type: application/json" \
  -d '{"text":"test"}'
```

---

## Integration Examples

### Command Center Integration
```python
from trinity_voice import TrinityVoiceSystem

voice = TrinityVoiceSystem()
voice.announce_action('command_center')
```

### VR Workspace Integration (JavaScript)
```javascript
// In vr_workspace_wireless.html
async function announceAction(action, detail = '') {
    await fetch('/api/speak', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action, detail})
    });
}

// Use throughout VR workspace
announceAction('cad_generating');
announceAction('cad_complete', '5 models generated');
```

---

**Status:** ✅ Voice system operational with system voice
**Upgrade:** Add Azure credentials for premium Microsoft AVA neural voice
**Next:** Test voice from Quest VR workspace
