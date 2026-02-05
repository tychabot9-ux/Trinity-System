#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════╗
║              TRINITY VR WORKSPACE SERVER                       ║
║           Oculus Quest 1 Engineering Interface                 ║
║                  v1.0 - February 2026                          ║
╚════════════════════════════════════════════════════════════════╝

VR Server for Trinity Engineering Station
- Serves WebXR/A-Frame VR workspace
- Integrates with Trinity CAD generation
- Supports Oculus Quest 1 via USB-C
- Real-time model loading and manipulation
"""

import os
import json
import time
import logging
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime
import subprocess

# Configuration
VR_PORT = 8503
BASE_DIR = Path(__file__).parent
CAD_OUTPUT_DIR = BASE_DIR / "cad_output"
VR_WORKSPACE_FILE = BASE_DIR / "vr_workspace_wireless.html"
LOG_DIR = BASE_DIR / "logs"

# Ensure directories exist
CAD_OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'vr_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Server stats
SERVER_START_TIME = time.time()
REQUEST_COUNT = 0
ACTIVE_CONNECTIONS = 0

class TrinityVRHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for Trinity VR Workspace."""

    def __init__(self, *args, **kwargs):
        # Set the directory to serve from
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        global REQUEST_COUNT
        REQUEST_COUNT += 1

        parsed_path = urlparse(self.path)
        logger.info(f"GET {parsed_path.path} from {self.client_address[0]}")

        # Serve main VR workspace
        if parsed_path.path == '/' or parsed_path.path == '/vr':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(VR_WORKSPACE_FILE, 'rb') as f:
                self.wfile.write(f.read())
            return

        # Server status endpoint
        elif parsed_path.path == '/api/status':
            uptime = time.time() - SERVER_START_TIME
            status = {
                'status': 'online',
                'uptime': uptime,
                'uptime_human': f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m",
                'requests': REQUEST_COUNT,
                'models_count': len(list(CAD_OUTPUT_DIR.glob('*.stl'))),
                'timestamp': datetime.now().isoformat(),
                'version': '1.0',
                'wireless': True,
                'network': {
                    'tailscale': self._get_tailscale_ip(),
                    'local': self._get_local_ip()
                }
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(status).encode())
            return

        # List available models
        elif parsed_path.path == '/api/models':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            models = []
            for file in CAD_OUTPUT_DIR.glob('*.stl'):
                models.append({
                    'name': file.name,
                    'path': f'/cad_output/{file.name}',
                    'size': file.stat().st_size,
                    'modified': file.stat().st_mtime
                })

            self.wfile.write(json.dumps(models).encode())
            return

        # Default file serving
        else:
            # Add CORS headers for cross-origin requests
            super().do_GET()

    def _get_tailscale_ip(self):
        """Get Tailscale IP address."""
        try:
            result = subprocess.run(['tailscale', 'ip', '-4'],
                                  capture_output=True, text=True, timeout=2)
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None

    def _get_local_ip(self):
        """Get local WiFi IP address."""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return None

    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)

        # Generate CAD model endpoint
        if parsed_path.path == '/api/generate_cad':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode())
                prompt = data.get('prompt', 'hex bolt')

                # TODO: Integrate with Trinity CAD generation
                # For now, return test model
                response = {
                    'status': 'success',
                    'filename': 'test_bolt.stl',
                    'message': f'Generating: {prompt}'
                }

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())

            except Exception as e:
                self.send_error(500, f'Error: {str(e)}')

            return

        self.send_error(404, 'Endpoint not found')

    def end_headers(self):
        """Add CORS headers to all responses."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def log_message(self, format, *args):
        """Custom logging."""
        print(f"[Trinity VR] {self.address_string()} - {format % args}")


def main():
    """Start Trinity VR Server."""
    print("╔════════════════════════════════════════╗")
    print("║    TRINITY VR WORKSPACE SERVER         ║")
    print("╚════════════════════════════════════════╝")
    print()
    print(f"🥽 Oculus Quest 1 Engineering Workspace")
    print(f"📡 Server starting on port {VR_PORT}...")
    print()
    print(f"🌐 VR Workspace: http://localhost:{VR_PORT}/vr")
    print(f"📱 Quest Access: http://[MAC-IP]:{VR_PORT}/vr")
    print()
    print("📦 CAD Output Directory:", CAD_OUTPUT_DIR)
    print("🔧 Status: Ready for VR")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 44)

    server = HTTPServer(('0.0.0.0', VR_PORT), TrinityVRHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Trinity VR Server stopped")
        server.shutdown()


if __name__ == '__main__':
    main()
