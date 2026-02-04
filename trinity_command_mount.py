#!/usr/bin/env python3
"""
Trinity Command Center - FastAPI Integration
Mounts the Streamlit command center into the existing FastAPI server.
"""

import subprocess
import time
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

# Start Streamlit in background
STREAMLIT_PORT = 8502
STREAMLIT_PROCESS = None

def start_streamlit_subprocess():
    """Start Streamlit as a subprocess."""
    global STREAMLIT_PROCESS

    command_center_py = Path(__file__).parent / "command_center.py"

    STREAMLIT_PROCESS = subprocess.Popen([
        "streamlit", "run",
        str(command_center_py),
        "--server.port", str(STREAMLIT_PORT),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--theme.base", "dark",
        "--theme.primaryColor", "#00FF00",
        "--theme.backgroundColor", "#0E1117",
        "--theme.secondaryBackgroundColor", "#262730"
    ])

    # Wait for Streamlit to start
    time.sleep(3)
    print(f"✅ Streamlit Command Center started on port {STREAMLIT_PORT}")

def stop_streamlit_subprocess():
    """Stop the Streamlit subprocess."""
    global STREAMLIT_PROCESS
    if STREAMLIT_PROCESS:
        STREAMLIT_PROCESS.terminate()
        STREAMLIT_PROCESS.wait()
        print("🛑 Streamlit Command Center stopped")

def mount_command_center(app: FastAPI):
    """Mount the command center into existing FastAPI app."""

    @app.on_event("startup")
    async def startup_command_center():
        """Start command center on app startup."""
        start_streamlit_subprocess()

    @app.on_event("shutdown")
    async def shutdown_command_center():
        """Stop command center on app shutdown."""
        stop_streamlit_subprocess()

    @app.get("/command")
    async def command_center_redirect(request: Request):
        """Redirect to command center with VR mode detection."""
        # Check if request is from VR device (Oculus)
        user_agent = request.headers.get('user-agent', '').lower()
        vr_param = "?vr=true" if 'oculus' in user_agent or 'quest' in user_agent else ""

        return RedirectResponse(url=f"http://localhost:{STREAMLIT_PORT}/{vr_param}")

    @app.get("/command/career")
    async def command_career():
        """Direct link to career station."""
        return RedirectResponse(url=f"http://localhost:{STREAMLIT_PORT}/?module=Career")

    @app.get("/command/engineering")
    async def command_engineering():
        """Direct link to engineering station."""
        return RedirectResponse(url=f"http://localhost:{STREAMLIT_PORT}/?module=Engineering")

    @app.get("/command/trading")
    async def command_trading():
        """Direct link to trading station."""
        return RedirectResponse(url=f"http://localhost:{STREAMLIT_PORT}/?module=Trading")

    print("✅ Trinity Command Center mounted at /command")

# Standalone mode for testing
if __name__ == "__main__":
    from fastapi import FastAPI

    app = FastAPI(title="Trinity Command Center Standalone")
    mount_command_center(app)

    print("=" * 70)
    print("  TRINITY COMMAND CENTER - STANDALONE MODE")
    print("=" * 70)
    print(f"  FastAPI:  http://localhost:8001")
    print(f"  Command:  http://localhost:8001/command")
    print(f"  Streamlit: http://localhost:{STREAMLIT_PORT}")
    print("=" * 70)

    uvicorn.run(app, host="0.0.0.0", port=8001)
