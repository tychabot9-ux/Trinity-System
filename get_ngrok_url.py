#!/usr/bin/env python3
"""
Get ngrok public URL for Quest VR access
"""
import requests
import json
import time
import sys

def get_ngrok_url():
    """Get the public ngrok URL."""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            if tunnels:
                for tunnel in tunnels:
                    if tunnel.get('proto') == 'https':
                        url = tunnel.get('public_url')
                        return url
                # If no https, get first one
                return tunnels[0].get('public_url')
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    return None

if __name__ == '__main__':
    print("Checking for ngrok tunnel...")
    url = get_ngrok_url()
    if url:
        print(f"✅ Ngrok URL: {url}")
        print(f"\nQuest VR Access: {url}/vr")
        sys.exit(0)
    else:
        print("❌ No ngrok tunnel found")
        print("Start ngrok with: ngrok http 8503")
        sys.exit(1)
