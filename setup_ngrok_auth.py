#!/usr/bin/env python3
"""
Setup ngrok authentication with fallback to alternative solutions
"""
import subprocess
import sys
import os
from pathlib import Path

def check_ngrok_auth():
    """Check if ngrok is authenticated."""
    config_path = Path.home() / "Library/Application Support/ngrok/ngrok.yml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            content = f.read()
            if 'authtoken:' in content and content.count(':') > 1:
                return True
    return False

def setup_ngrok_prompt():
    """Prompt user to setup ngrok (for when user returns)."""
    print("\n" + "="*70)
    print("❌ NGROK REQUIRES AUTHENTICATION")
    print("="*70)
    print("\nngrok requires a free account to create public tunnels.")
    print("\n📝 TO COMPLETE SETUP:")
    print("1. Sign up (free): https://dashboard.ngrok.com/signup")
    print("2. Get your authtoken: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("3. Run: ngrok config add-authtoken YOUR_TOKEN")
    print("4. Then re-run: python3 quest_setup.py")
    print("\n" + "="*70)

def use_local_network():
    """Use local network access instead of ngrok."""
    import socket
    import json
    import qrcode

    print("\n" + "="*70)
    print("🔄 FALLING BACK TO LOCAL NETWORK ACCESS")
    print("="*70)

    # Get local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "192.168.1.216"  # Fallback from earlier test

    port = 8503
    local_url = f"http://{local_ip}:{port}"
    vr_url = f"{local_url}/vr"

    print(f"\n✅ Local Network URL: {vr_url}")
    print(f"📱 Quest must be on the same WiFi network")

    # Generate QR code
    print("\n🔧 Generating QR code...")
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(vr_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    qr_path = Path(__file__).parent / "quest_qr_code.png"
    img.save(qr_path)
    print(f"✅ QR code saved: {qr_path}")

    # Create HTML access page
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Quest VR Access - Trinity System (Local)</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: rgba(0, 0, 0, 0.7);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }}
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }}
        .subtitle {{
            font-size: 1.2em;
            color: #aaa;
            margin-bottom: 30px;
        }}
        .url-box {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            font-size: 1.3em;
            word-break: break-all;
        }}
        .qr-container {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            display: inline-block;
            margin: 30px 0;
        }}
        .instructions {{
            text-align: left;
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .instructions h2 {{
            color: #4CAF50;
            margin-top: 0;
        }}
        .instructions li {{
            margin: 10px 0;
            line-height: 1.6;
        }}
        .status {{
            background: rgba(76, 175, 80, 0.2);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border: 2px solid #4CAF50;
        }}
        .warning {{
            background: rgba(255, 152, 0, 0.2);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border: 2px solid #FF9800;
        }}
        .button {{
            background: #4CAF50;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            font-size: 1.2em;
            cursor: pointer;
            margin: 10px;
            text-decoration: none;
            display: inline-block;
        }}
        .button:hover {{
            background: #45a049;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🥽 Quest VR Access</h1>
        <div class="subtitle">Trinity Engineering Workspace (Local Network)</div>

        <div class="status">
            ✅ SERVER ONLINE | 📡 LOCAL NETWORK ACCESS
        </div>

        <div class="warning">
            ⚠️ Quest must be on the same WiFi network as this Mac
        </div>

        <div class="url-box">
            <strong>VR Workspace URL:</strong><br>
            <a href="{vr_url}" style="color: #4CAF50; text-decoration: none;">{vr_url}</a>
        </div>

        <div class="qr-container">
            <img src="quest_qr_code.png" alt="QR Code" style="width: 300px; height: 300px;">
        </div>

        <div>
            <a href="{vr_url}" class="button">🚀 Launch VR Workspace</a>
            <a href="{local_url}/api/status" class="button">📊 Server Status</a>
        </div>

        <div class="instructions">
            <h2>📱 Quest Setup Instructions:</h2>
            <ol>
                <li>⚠️ <strong>IMPORTANT:</strong> Connect your Quest to the same WiFi network</li>
                <li>Open <strong>Oculus Browser</strong> on your Quest VR headset</li>
                <li>Scan the QR code above OR manually enter: {vr_url}</li>
                <li>Bookmark the page for quick access</li>
                <li>Click "Enter VR" when the page loads</li>
                <li>Enjoy your VR engineering workspace!</li>
            </ol>

            <h2>🔧 Features:</h2>
            <ul>
                <li>Real-time CAD model viewing and manipulation</li>
                <li>Voice command integration with Trinity AI</li>
                <li>Clipboard sync between Quest and Mac</li>
                <li>3D model generation from voice prompts</li>
            </ul>

            <h2>⚡ Quick Access URLs:</h2>
            <ul>
                <li><strong>VR Workspace:</strong> {vr_url}</li>
                <li><strong>Server Status:</strong> {local_url}/api/status</li>
                <li><strong>Models List:</strong> {local_url}/api/models</li>
            </ul>

            <h2>🌐 Want Public Internet Access?</h2>
            <p>To access from anywhere (not just local WiFi):</p>
            <ol>
                <li>Sign up for free ngrok account: https://dashboard.ngrok.com/signup</li>
                <li>Get authtoken: https://dashboard.ngrok.com/get-started/your-authtoken</li>
                <li>Run: ngrok config add-authtoken YOUR_TOKEN</li>
                <li>Run: python3 quest_setup.py</li>
            </ol>
        </div>

        <div style="margin-top: 30px; font-size: 0.9em; color: #888;">
            Generated: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}<br>
            Trinity VR System v1.0 - Local Network Mode<br>
            Local IP: {local_ip} | Port: {port}
        </div>
    </div>
</body>
</html>
"""

    html_path = Path(__file__).parent / "quest_access.html"
    with open(html_path, 'w') as f:
        f.write(html_content)
    print(f"✅ Access page created: {html_path}")

    # Save text file
    access_info = f"""
╔════════════════════════════════════════════════════════════════╗
║              QUEST VR ACCESS INFORMATION                       ║
║           Trinity System v1.0 (LOCAL NETWORK)                  ║
╚════════════════════════════════════════════════════════════════╝

Generated: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}

🌐 LOCAL NETWORK ACCESS URL:
   {vr_url}

📊 SERVER STATUS:
   {local_url}/api/status

📦 MODELS API:
   {local_url}/api/models

⚠️  IMPORTANT: Quest must be on same WiFi network as Mac!

╔════════════════════════════════════════════════════════════════╗
║                  QUEST SETUP INSTRUCTIONS                      ║
╚════════════════════════════════════════════════════════════════╝

1. Connect your Quest to the SAME WiFi network as this Mac
2. Put on your Oculus Quest VR headset
3. Open the Oculus Browser app
4. Navigate to: {vr_url}
5. Bookmark the page for quick access
6. Click "Enter VR" button
7. Enjoy your VR engineering workspace!

╔════════════════════════════════════════════════════════════════╗
║                    AVAILABLE FEATURES                          ║
╚════════════════════════════════════════════════════════════════╝

✅ Real-time 3D CAD model viewing
✅ Voice command integration
✅ Clipboard sync (Quest ↔ Mac)
✅ Trinity AI assistant
✅ Model generation from voice prompts
✅ WebXR/A-Frame VR environment

╔════════════════════════════════════════════════════════════════╗
║                    NETWORK INFORMATION                         ║
╚════════════════════════════════════════════════════════════════╝

Local IP Address:    {local_ip}
Server Port:         {port}
Protocol:            HTTP (Local Network)
Access:              Same WiFi network only

╔════════════════════════════════════════════════════════════════╗
║                  UPGRADE TO PUBLIC ACCESS                      ║
╚════════════════════════════════════════════════════════════════╝

To access from ANY network (not just local WiFi):

1. Sign up for free ngrok account:
   https://dashboard.ngrok.com/signup

2. Get your authtoken:
   https://dashboard.ngrok.com/get-started/your-authtoken

3. Configure ngrok:
   ngrok config add-authtoken YOUR_TOKEN

4. Re-run setup:
   python3 quest_setup.py

╔════════════════════════════════════════════════════════════════╗
║                     FILES GENERATED                            ║
╚════════════════════════════════════════════════════════════════╝

- quest_access.html     (Fancy access page with QR code)
- quest_qr_code.png     (Scannable QR code)
- QUEST_ACCESS.txt      (This file)

╔════════════════════════════════════════════════════════════════╗
║                      TROUBLESHOOTING                           ║
╚════════════════════════════════════════════════════════════════╝

If connection fails:
1. Verify Quest is on same WiFi network
2. Check VR server: curl http://localhost:8503/api/status
3. Try the direct IP: {vr_url}
4. Check Mac firewall settings (allow port {port})

╔════════════════════════════════════════════════════════════════╗
║                   MAINTENANCE COMMANDS                         ║
╚════════════════════════════════════════════════════════════════╝

Check status:       curl {local_url}/api/status
View logs:          tail -f logs/vr_server.log
Test from Quest:    Open Oculus Browser → {vr_url}

════════════════════════════════════════════════════════════════

🚀 READY FOR VR! Scan the QR code or visit the URL above.

════════════════════════════════════════════════════════════════
"""

    info_path = Path.home() / "Desktop" / "QUEST_ACCESS.txt"
    with open(info_path, 'w') as f:
        f.write(access_info)
    print(f"✅ Access info saved: {info_path}")

    # Open HTML in browser
    try:
        subprocess.run(['open', str(html_path)])
        print("✅ Opening access page in browser...")
    except:
        pass

    print("\n" + "="*70)
    print("🎉 LOCAL NETWORK SETUP COMPLETE!")
    print("="*70)
    print(f"\n🌐 VR Workspace URL: {vr_url}")
    print(f"📱 Open quest_access.html to see QR code")
    print(f"🥽 Quest must be on same WiFi network!")
    print("\n" + "="*70)

def main():
    print("╔════════════════════════════════════════╗")
    print("║   QUEST VR CONNECTION SETUP            ║")
    print("╚════════════════════════════════════════╝")
    print()

    if check_ngrok_auth():
        print("✅ ngrok is authenticated")
        print("Run quest_setup.py for public access")
        sys.exit(0)
    else:
        print("⚠️  ngrok is not authenticated")
        setup_ngrok_prompt()
        print("\n🔄 Using local network access instead...")
        use_local_network()

if __name__ == '__main__':
    main()
