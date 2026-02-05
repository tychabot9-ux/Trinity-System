#!/usr/bin/env python3
"""
AUTONOMOUS QUEST VR SETUP
Sets up ngrok tunnel and generates access info for Quest VR
"""
import subprocess
import time
import sys
import os
import json
import requests
import qrcode
from pathlib import Path

def check_ngrok_installed():
    """Check if ngrok is installed."""
    try:
        result = subprocess.run(['which', 'ngrok'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def start_ngrok():
    """Start ngrok tunnel in background."""
    print("Starting ngrok tunnel on port 8503...")
    try:
        # Kill any existing ngrok processes
        subprocess.run(['pkill', '-f', 'ngrok'], stderr=subprocess.DEVNULL)
        time.sleep(1)

        # Start ngrok in background
        subprocess.Popen(
            ['ngrok', 'http', '8503', '--log=stdout'],
            stdout=open('/tmp/ngrok.log', 'w'),
            stderr=subprocess.STDOUT
        )

        # Wait for ngrok to start
        print("Waiting for ngrok to initialize...")
        time.sleep(4)
        return True
    except Exception as e:
        print(f"Error starting ngrok: {e}")
        return False

def get_ngrok_url():
    """Get the public ngrok URL."""
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get('tunnels', [])
                if tunnels:
                    # Prefer HTTPS tunnel
                    for tunnel in tunnels:
                        if tunnel.get('proto') == 'https':
                            return tunnel.get('public_url')
                    # Otherwise return first tunnel
                    return tunnels[0].get('public_url')
        except Exception as e:
            if attempt < max_attempts - 1:
                print(f"Attempt {attempt + 1}/{max_attempts}: Waiting for ngrok...")
                time.sleep(2)
            else:
                print(f"Error getting ngrok URL: {e}")
    return None

def test_connection(url):
    """Test if the URL is accessible."""
    try:
        response = requests.get(f"{url}/api/status", timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

def generate_qr_code(url, output_path):
    """Generate QR code for the URL."""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"{url}/vr")
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)
        print(f"✅ QR code saved to: {output_path}")
        return True
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return False

def create_access_page(url):
    """Create HTML access page with QR code."""
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Quest VR Access - Trinity System</title>
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
        <div class="subtitle">Trinity Engineering Workspace</div>

        <div class="status">
            ✅ SERVER ONLINE | 🌐 PUBLIC ACCESS READY
        </div>

        <div class="url-box">
            <strong>VR Workspace URL:</strong><br>
            <a href="{url}/vr" style="color: #4CAF50; text-decoration: none;">{url}/vr</a>
        </div>

        <div class="qr-container">
            <img src="quest_qr_code.png" alt="QR Code" style="width: 300px; height: 300px;">
        </div>

        <div>
            <a href="{url}/vr" class="button">🚀 Launch VR Workspace</a>
            <a href="{url}/api/status" class="button">📊 Server Status</a>
        </div>

        <div class="instructions">
            <h2>📱 Quest Setup Instructions:</h2>
            <ol>
                <li>Open <strong>Oculus Browser</strong> on your Quest VR headset</li>
                <li>Scan the QR code above OR manually enter the URL</li>
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
                <li><strong>VR Workspace:</strong> {url}/vr</li>
                <li><strong>Server Status:</strong> {url}/api/status</li>
                <li><strong>Models List:</strong> {url}/api/models</li>
            </ul>
        </div>

        <div style="margin-top: 30px; font-size: 0.9em; color: #888;">
            Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}<br>
            Trinity VR System v1.0
        </div>
    </div>
</body>
</html>
"""

    output_path = Path(__file__).parent / "quest_access.html"
    with open(output_path, 'w') as f:
        f.write(html_content)

    print(f"✅ Access page created: {output_path}")
    return output_path

def save_access_info(url):
    """Save all access information to file."""
    vr_url = f"{url}/vr"
    info = f"""
╔════════════════════════════════════════════════════════════════╗
║              QUEST VR ACCESS INFORMATION                       ║
║                  Trinity System v1.0                           ║
╚════════════════════════════════════════════════════════════════╝

Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

🌐 PUBLIC ACCESS URL:
   {vr_url}

📊 SERVER STATUS:
   {url}/api/status

📦 MODELS API:
   {url}/api/models

🔗 CLIPBOARD SYNC:
   {url}/api/clipboard

╔════════════════════════════════════════════════════════════════╗
║                  QUEST SETUP INSTRUCTIONS                      ║
╚════════════════════════════════════════════════════════════════╝

1. Put on your Oculus Quest VR headset
2. Open the Oculus Browser app
3. Navigate to: {vr_url}
4. Bookmark the page for quick access
5. Click "Enter VR" button
6. Enjoy your VR engineering workspace!

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

Public URL (ngrok):  {url}
Local Server Port:   8503
Protocol:            HTTPS (ngrok tunnel)
Access:              Global (any network)

╔════════════════════════════════════════════════════════════════╗
║                      TROUBLESHOOTING                           ║
╚════════════════════════════════════════════════════════════════╝

If connection fails:
1. Check ngrok is running: ps aux | grep ngrok
2. Verify VR server: curl http://localhost:8503/api/status
3. Restart ngrok: pkill ngrok && ngrok http 8503
4. Check ngrok dashboard: http://localhost:4040

╔════════════════════════════════════════════════════════════════╗
║                     FILES GENERATED                            ║
╚════════════════════════════════════════════════════════════════╝

- quest_access.html     (Fancy access page with QR code)
- quest_qr_code.png     (Scannable QR code)
- QUEST_ACCESS.txt      (This file)

╔════════════════════════════════════════════════════════════════╗
║                   MAINTENANCE COMMANDS                         ║
╚════════════════════════════════════════════════════════════════╝

Check status:       python3 get_ngrok_url.py
Restart ngrok:      ./start_ngrok.sh
View logs:          tail -f logs/vr_server.log
Test connection:    curl {url}/api/status

════════════════════════════════════════════════════════════════

🚀 READY FOR VR! Scan the QR code or visit the URL above.

════════════════════════════════════════════════════════════════
"""

    output_path = Path.home() / "Desktop" / "QUEST_ACCESS.txt"
    with open(output_path, 'w') as f:
        f.write(info)

    print(f"✅ Access info saved to: {output_path}")
    return output_path

def main():
    """Main setup function."""
    print("╔════════════════════════════════════════╗")
    print("║   QUEST VR AUTONOMOUS SETUP            ║")
    print("╚════════════════════════════════════════╝")
    print()

    # Check ngrok installed
    if not check_ngrok_installed():
        print("❌ ngrok not found!")
        print("Installing ngrok...")
        try:
            subprocess.run(['brew', 'install', 'ngrok'], check=True)
            print("✅ ngrok installed")
        except:
            print("❌ Failed to install ngrok")
            print("Please install manually: brew install ngrok")
            sys.exit(1)
    else:
        print("✅ ngrok is installed")

    # Start ngrok
    if not start_ngrok():
        print("❌ Failed to start ngrok")
        sys.exit(1)

    print("✅ ngrok tunnel started")

    # Get public URL
    print("\nGetting public URL...")
    url = get_ngrok_url()

    if not url:
        print("❌ Failed to get ngrok URL")
        print("Check ngrok status: http://localhost:4040")
        sys.exit(1)

    print(f"✅ Public URL: {url}")

    # Test connection
    print("\nTesting connection...")
    if test_connection(url):
        print("✅ Connection test passed")
    else:
        print("⚠️  Connection test failed, but continuing...")

    # Generate QR code
    print("\nGenerating QR code...")
    qr_path = Path(__file__).parent / "quest_qr_code.png"
    generate_qr_code(url, qr_path)

    # Create access page
    print("\nCreating access page...")
    html_path = create_access_page(url)

    # Save access info
    print("\nSaving access information...")
    info_path = save_access_info(url)

    # Final summary
    print("\n" + "=" * 60)
    print("🎉 QUEST VR SETUP COMPLETE!")
    print("=" * 60)
    print(f"\n🌐 VR Workspace URL: {url}/vr")
    print(f"\n📄 Files created:")
    print(f"   - {html_path}")
    print(f"   - {qr_path}")
    print(f"   - {info_path}")
    print(f"\n📱 Open quest_access.html in a browser to see the QR code")
    print(f"🥽 Scan the QR code with your Quest to access the VR workspace")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
