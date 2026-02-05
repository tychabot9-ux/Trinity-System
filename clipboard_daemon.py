#!/usr/bin/env python3
"""
Trinity Universal Clipboard Daemon
Background service for Mac ↔ Quest clipboard sync
Works like iPhone ↔ Mac Universal Clipboard
"""

import os
import time
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

# Configuration
SYNC_FILE = Path.home() / ".trinity_clipboard"
CHECK_INTERVAL = 1  # Check every second
LOG_FILE = Path("/tmp/trinity_clipboard.log")

def log(message):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} - {message}\n")

def get_mac_clipboard():
    """Get current Mac clipboard content."""
    try:
        result = subprocess.run(['pbpaste'], capture_output=True, text=True, timeout=1)
        return result.stdout
    except:
        return ""

def set_mac_clipboard(text):
    """Set Mac clipboard content."""
    try:
        subprocess.run(['pbcopy'], input=text.encode(), timeout=1)
        return True
    except:
        return False

def get_clipboard_hash(text):
    """Get hash of clipboard content."""
    return hashlib.md5(text.encode()).hexdigest()

def read_sync_file():
    """Read synced clipboard from file."""
    try:
        if SYNC_FILE.exists():
            with open(SYNC_FILE, 'r') as f:
                return json.load(f)
        return {}
    except:
        return {}

def write_sync_file(data):
    """Write clipboard to sync file."""
    try:
        with open(SYNC_FILE, 'w') as f:
            json.dump(data, f)
        return True
    except:
        return False

def main():
    """Main clipboard sync loop."""
    log("Trinity Clipboard Daemon started")

    last_mac_hash = ""
    last_sync_hash = ""

    print("Trinity Clipboard Daemon running...")
    print(f"Sync file: {SYNC_FILE}")
    print(f"Check interval: {CHECK_INTERVAL}s")
    print("Press Ctrl+C to stop")

    try:
        while True:
            # Get current Mac clipboard
            mac_content = get_mac_clipboard()
            mac_hash = get_clipboard_hash(mac_content)

            # Read sync file
            sync_data = read_sync_file()
            sync_content = sync_data.get('content', '')
            sync_hash = get_clipboard_hash(sync_content)

            # If Mac clipboard changed, update sync file
            if mac_hash != last_mac_hash and mac_hash != sync_hash and mac_content:
                sync_data = {
                    'content': mac_content,
                    'source': 'mac',
                    'timestamp': datetime.now().isoformat(),
                    'hash': mac_hash
                }
                if write_sync_file(sync_data):
                    log(f"Mac → Sync: {len(mac_content)} chars")
                    last_mac_hash = mac_hash

            # If sync file changed (from Quest), update Mac clipboard
            elif sync_hash != last_sync_hash and sync_hash != mac_hash and sync_content:
                if sync_data.get('source') != 'mac':  # Don't copy back our own changes
                    if set_mac_clipboard(sync_content):
                        log(f"Sync → Mac: {len(sync_content)} chars")
                        last_sync_hash = sync_hash
                        last_mac_hash = sync_hash

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        log("Trinity Clipboard Daemon stopped")
        print("\nStopped")

if __name__ == '__main__':
    main()
