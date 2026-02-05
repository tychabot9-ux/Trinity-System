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
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import subprocess

# Configuration
VR_PORT = 8503
BASE_DIR = Path(__file__).parent
CAD_OUTPUT_DIR = BASE_DIR / "cad_output"
VR_WORKSPACE_FILE = BASE_DIR / "vr_workspace.html"

# Ensure directories exist
CAD_OUTPUT_DIR.mkdir(exist_ok=True)

class TrinityVRHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for Trinity VR Workspace."""

    def __init__(self, *args, **kwargs):
        # Set the directory to serve from
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)

        # Serve main VR workspace
        if parsed_path.path == '/' or parsed_path.path == '/vr':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(VR_WORKSPACE_FILE, 'rb') as f:
                self.wfile.write(f.read())
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
