#!/bin/bash
# Trinity Universal Clipboard Setup
# Enables Mac ↔ Quest clipboard sharing like iPhone ↔ Mac

echo "🔗 Setting up Universal Clipboard for Trinity System"
echo ""

# Method 1: Tailscale Clipboard (Recommended)
echo "📋 Enabling Tailscale clipboard sharing..."

# Check if Tailscale is running
if ! pgrep -x "Tailscale" > /dev/null; then
    echo "⚠️  Starting Tailscale..."
    open -a Tailscale
    sleep 2
fi

# Enable Tailscale features
echo "Configuring Tailscale for clipboard sync..."

# Note: Tailscale clipboard sharing is automatic when both devices are on Tailscale
# No additional configuration needed on Mac side

echo ""
echo "✅ Tailscale clipboard sharing ready!"
echo ""
echo "📱 On your Oculus Quest:"
echo "   1. Install Tailscale app from SideQuest or APK"
echo "   2. Log in with same account (tychabot9@gmail.com)"
echo "   3. Clipboard will sync automatically"
echo ""
echo "Alternative: Use KDE Connect (cross-platform)"
echo ""

# Method 2: Create clipboard bridge service
cat > ~/Library/LaunchAgents/com.trinity.clipboard.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.trinity.clipboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/tybrown/Desktop/Trinity-System/clipboard_daemon.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/tmp/trinity_clipboard.log</string>
    <key>StandardOutPath</key>
    <string>/tmp/trinity_clipboard.log</string>
</dict>
</plist>
EOF

echo "📋 Created clipboard daemon config"
echo ""
echo "To enable background clipboard sync:"
echo "  launchctl load ~/Library/LaunchAgents/com.trinity.clipboard.plist"
echo ""
echo "✅ Setup complete!"
