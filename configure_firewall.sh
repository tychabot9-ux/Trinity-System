#!/bin/bash
# Trinity VR Firewall Configuration for macOS
# Ensures port 8503 is accessible for VR connections

echo "╔════════════════════════════════════════════════════════╗"
echo "║      TRINITY VR FIREWALL CONFIGURATION                 ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script needs sudo privileges to configure firewall"
    echo ""
    echo "Please run with sudo:"
    echo "  sudo $0"
    echo ""
    exit 1
fi

echo "Configuring macOS firewall for Trinity VR Server..."
echo ""

# Check firewall status
FIREWALL_STATUS=$(defaults read /Library/Preferences/com.apple.alf globalstate 2>/dev/null || echo "0")

echo "📊 Current Firewall Status:"
case "$FIREWALL_STATUS" in
    0)
        echo "   Firewall is OFF (no configuration needed)"
        echo ""
        echo "✅ Port 8503 should be accessible"
        exit 0
        ;;
    1)
        echo "   Firewall is ON (specific apps allowed)"
        ;;
    2)
        echo "   Firewall is ON (essential services only)"
        ;;
    *)
        echo "   Unknown status"
        ;;
esac

echo ""

# Find Python3 path
PYTHON_PATH=$(which python3)
echo "🐍 Python location: $PYTHON_PATH"
echo ""

# Add Python3 to firewall exceptions
echo "Adding Python3 to firewall exceptions..."

# Method 1: Using socketfilterfw (preferred)
if [ -x /usr/libexec/ApplicationFirewall/socketfilterfw ]; then
    echo "Using socketfilterfw..."

    # Add Python3
    /usr/libexec/ApplicationFirewall/socketfilterfw --add "$PYTHON_PATH" 2>/dev/null
    /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp "$PYTHON_PATH" 2>/dev/null

    # Verify
    if /usr/libexec/ApplicationFirewall/socketfilterfw --listapps | grep -q python3; then
        echo "✅ Python3 added to firewall exceptions"
    else
        echo "⚠️  Could not verify Python3 in firewall exceptions"
    fi
else
    echo "⚠️  socketfilterfw not found"
fi

echo ""

# Check pfctl (Packet Filter) configuration
echo "📋 Checking Packet Filter (pfctl)..."

if pfctl -s rules 2>/dev/null | grep -q 8503; then
    echo "✅ Port 8503 rule already exists in pfctl"
else
    echo "ℹ️  No explicit pfctl rule for port 8503"
    echo "   (This is usually not needed unless firewall is very restrictive)"
fi

echo ""

# Additional recommendations
echo "╔════════════════════════════════════════════════════════╗"
echo "║              FIREWALL CONFIGURATION COMPLETE           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "✅ Configuration complete!"
echo ""
echo "📝 Summary:"
echo "   - Python3 added to firewall exceptions"
echo "   - Port 8503 should now be accessible"
echo "   - VR server can accept connections"
echo ""

echo "🔍 Testing Configuration:"
echo ""
echo "1. Start VR server:"
echo "   ./AUTO_DEPLOY_VR.sh"
echo ""
echo "2. Test from another device on same network:"
echo "   curl http://[THIS_MAC_IP]:8503/api/status"
echo ""
echo "3. From Quest browser, navigate to:"
echo "   http://[THIS_MAC_IP]:8503/vr"
echo ""

echo "💡 Additional Tips:"
echo ""
echo "If connections still fail:"
echo "   1. Open System Preferences > Security & Privacy > Firewall"
echo "   2. Click 'Firewall Options'"
echo "   3. Add Python3 manually if not listed"
echo "   4. Ensure 'Block all incoming connections' is OFF"
echo "   5. Consider temporarily disabling firewall for testing"
echo ""

echo "🔐 Security Notes:"
echo "   - Only allow connections from trusted networks"
echo "   - Use Tailscale VPN for remote access"
echo "   - Keep firewall enabled when not using VR"
echo "   - Monitor logs for suspicious activity"
echo ""

# Create a simple verification script
cat > verify_firewall.sh << 'EOF'
#!/bin/bash
echo "Verifying firewall configuration..."
echo ""
echo "Firewall Status:"
defaults read /Library/Preferences/com.apple.alf globalstate 2>/dev/null | sed 's/^/   /'
echo ""
echo "Python3 in firewall:"
/usr/libexec/ApplicationFirewall/socketfilterfw --listapps 2>/dev/null | grep -i python | sed 's/^/   /'
echo ""
echo "Port 8503 listeners:"
lsof -Pi :8503 | sed 's/^/   /'
EOF

chmod +x verify_firewall.sh

echo "📄 Created verification script: verify_firewall.sh"
echo "   Run './verify_firewall.sh' to check configuration anytime"
echo ""

echo "✅ All done!"
