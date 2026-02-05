# Trinity Universal Clipboard
## Mac ↔ Quest Clipboard Sync (Like iPhone ↔ Mac)

### How It Works
The Trinity clipboard system provides automatic clipboard sharing between your Mac and Oculus Quest, just like Universal Clipboard works between iPhone and Mac.

### Architecture
```
Mac Clipboard (pbcopy/pbpaste)
         ↕
Clipboard Daemon (Python)
         ↕
Sync File (~/.trinity_clipboard)
         ↕
VR Server API (HTTP)
         ↕
Quest Browser (JavaScript)
```

### API Endpoints

#### GET /api/clipboard
Read clipboard content from Mac.

**Request:**
```javascript
fetch('http://192.168.1.216:8503/api/clipboard')
  .then(r => r.json())
  .then(data => console.log(data.content));
```

**Response:**
```json
{
  "content": "Clipboard text here",
  "source": "mac",
  "timestamp": "2026-02-04T17:00:00.000000",
  "hash": "abc123..."
}
```

#### POST /api/clipboard
Send clipboard content from Quest to Mac.

**Request:**
```javascript
fetch('http://192.168.1.216:8503/api/clipboard', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({content: 'Text copied from Quest'})
})
.then(r => r.json())
.then(data => console.log(data.message));
```

**Response:**
```json
{
  "status": "success",
  "message": "Clipboard synced to Mac",
  "chars": 23,
  "timestamp": "2026-02-04T17:00:00.000000"
}
```

### JavaScript Integration for VR Workspace

Add this to your VR workspace for clipboard features:

```javascript
// Copy text to Mac clipboard
async function copyToMac(text) {
    const response = await fetch('http://192.168.1.216:8503/api/clipboard', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({content: text})
    });
    const result = await response.json();
    console.log('Copied to Mac:', result.message);
    return result.status === 'success';
}

// Read text from Mac clipboard
async function pasteFromMac() {
    const response = await fetch('http://192.168.1.216:8503/api/clipboard');
    const data = await response.json();
    return data.content;
}

// Auto-sync: Poll Mac clipboard every 2 seconds
setInterval(async () => {
    const macClipboard = await pasteFromMac();
    // Update VR UI with clipboard content
    document.getElementById('clipboardDisplay').textContent = macClipboard;
}, 2000);
```

### Background Services

Both services must be running for clipboard sync:

1. **VR Server** (provides API endpoints)
   ```bash
   python3 /Users/tybrown/Desktop/Trinity-System/vr_server.py &
   ```

2. **Clipboard Daemon** (syncs Mac clipboard ↔ sync file)
   ```bash
   python3 /Users/tybrown/Desktop/Trinity-System/clipboard_daemon.py &
   ```

### Check Service Status

```bash
# Check VR server
curl http://localhost:8503/api/status

# Check clipboard daemon
tail -f /tmp/trinity_clipboard.log

# Test clipboard sync
echo "Test from Mac" | pbcopy
curl http://localhost:8503/api/clipboard | jq '.content'
```

### Sync Timing
- Daemon checks every 1 second
- API calls are instant
- Allow 1-2 seconds for changes to propagate

### Troubleshooting

**Clipboard not syncing:**
```bash
# Restart clipboard daemon
pkill -f clipboard_daemon.py
python3 /Users/tybrown/Desktop/Trinity-System/clipboard_daemon.py &

# Check logs
tail -20 /tmp/trinity_clipboard.log
```

**API not responding:**
```bash
# Restart VR server
pkill -f vr_server.py
python3 /Users/tybrown/Desktop/Trinity-System/vr_server.py &
```

**Test full roundtrip:**
```bash
# Mac → Quest
echo "From Mac!" | pbcopy
sleep 2
curl http://localhost:8503/api/clipboard | jq '.content'

# Quest → Mac
curl -X POST -H "Content-Type: application/json" \
  -d '{"content":"From Quest!"}' \
  http://localhost:8503/api/clipboard
sleep 2
pbpaste
```

### Access URLs

The clipboard API is available at:
- **Tailscale:** http://100.66.103.8:8503/api/clipboard
- **Local WiFi:** http://192.168.1.216:8503/api/clipboard
- **Localhost:** http://localhost:8503/api/clipboard

Use the Tailscale URL for secure access from anywhere on your Tailscale network.

### Next Steps

1. Add clipboard UI to VR workspace (text input field + copy/paste buttons)
2. Implement voice-to-text for VR text entry
3. Add clipboard history (last 10 items)
4. Support rich text/images in clipboard

---

**Status:** ✅ Fully operational
**Tested:** 2026-02-04
**Services:** Running in background
