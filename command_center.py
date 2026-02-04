#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════╗
║                  TRINITY COMMAND CENTER                        ║
║                  Unified AI Workstation                        ║
║                  v1.0 - February 2026                          ║
╚════════════════════════════════════════════════════════════════╝

Modules:
  🎯 Career Station - Job hunting automation
  🔧 Engineering Station - CAD generation & 3D modeling
  📊 Trading Station - Bot monitoring & performance

Access Points:
  Desktop: http://localhost:8001/command
  Mobile:  http://[TAILSCALE-IP]:8001/command
  VR:      http://[TAILSCALE-IP]:8001/command?vr=true
"""

import os
import sys
import json
import time
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sqlite3

import streamlit as st
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent
BOT_FACTORY_DIR = BASE_DIR.parent / "Bot-Factory"

# API Configuration
TRINITY_API_BASE = os.getenv("TRINITY_API_BASE", "http://localhost:8001")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# File paths
JOB_STATUS_DB = BASE_DIR / "job_status.db"
DRAFT_DIR = BASE_DIR / "email_drafts"
CAD_OUTPUT_DIR = BASE_DIR / "cad_output"
CAD_PREVIEWS_DIR = CAD_OUTPUT_DIR / "previews"

# Trading bot paths
PHOENIX_LOG = BOT_FACTORY_DIR / "mark_xii_phoenix.log"
GENESIS_LOG = BOT_FACTORY_DIR / "mark_xi_genesis.log"
MACRO_STATUS = BOT_FACTORY_DIR / "macro_status.json"

# Ensure directories exist
CAD_OUTPUT_DIR.mkdir(exist_ok=True)
CAD_PREVIEWS_DIR.mkdir(exist_ok=True)
DRAFT_DIR.mkdir(exist_ok=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'vr_mode' not in st.session_state:
        st.session_state.vr_mode = False
    if 'active_module' not in st.session_state:
        st.session_state.active_module = "Career"
    if 'last_cad_render' not in st.session_state:
        st.session_state.last_cad_render = None
    if 'ai_memory' not in st.session_state:
        st.session_state.ai_memory = []

# ============================================================================
# VR MODE UTILITIES
# ============================================================================

def is_vr_mode() -> bool:
    """Check if VR mode is enabled."""
    # Check URL parameter first
    query_params = st.query_params
    if 'vr' in query_params and query_params['vr'] == 'true':
        st.session_state.vr_mode = True
    return st.session_state.vr_mode

def get_display_config() -> Dict:
    """Get display configuration based on VR mode."""
    if is_vr_mode():
        return {
            'font_size': 'large',
            'button_size': 'large',
            'max_triangles': 5000,  # Simplified meshes for Quest 1
            'use_previews': True,   # Use PNG previews instead of live 3D
            'layout': 'wide',
            'sidebar_collapsed': False,
            'update_interval': 5000  # Slower updates to save battery
        }
    else:
        return {
            'font_size': 'normal',
            'button_size': 'normal',
            'max_triangles': 50000,
            'use_previews': False,
            'layout': 'wide',
            'sidebar_collapsed': False,
            'update_interval': 2000
        }

# ============================================================================
# JOB HUNTING MODULE
# ============================================================================

def get_job_statistics() -> Dict:
    """Get job application statistics from database."""
    try:
        conn = sqlite3.connect(JOB_STATUS_DB)
        cursor = conn.cursor()

        cursor.execute("SELECT status, COUNT(*) FROM job_statuses GROUP BY status")
        status_counts = dict(cursor.fetchall())

        cursor.execute("SELECT COUNT(*) FROM job_statuses WHERE applied_date >= date('now', '-7 days')")
        recent_apps = cursor.fetchone()[0]

        conn.close()

        return {
            'pending': status_counts.get('pending', 0),
            'applied': status_counts.get('applied', 0),
            'denied': status_counts.get('denied', 0),
            'recent_7_days': recent_apps,
            'total': sum(status_counts.values())
        }
    except Exception as e:
        return {
            'pending': 0,
            'applied': 0,
            'denied': 0,
            'recent_7_days': 0,
            'total': 0,
            'error': str(e)
        }

def get_recent_jobs(limit: int = 10) -> List[Dict]:
    """Get recent job applications."""
    try:
        conn = sqlite3.connect(JOB_STATUS_DB)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT company, position, status, fit_score, created_date, draft_filename
            FROM job_statuses
            ORDER BY created_date DESC
            LIMIT ?
        """, (limit,))

        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                'company': row[0],
                'position': row[1],
                'status': row[2],
                'fit_score': row[3],
                'created_date': row[4],
                'draft_filename': row[5]
            })

        conn.close()
        return jobs
    except Exception as e:
        return []

def submit_job_url(url: str) -> Dict:
    """Submit a job URL to Trinity for processing."""
    try:
        response = requests.post(
            f"{TRINITY_API_BASE}/api/submit-job",
            json={"url": url},
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def render_career_station():
    """Render the Career/Job Hunting module."""
    st.header("🎯 Career Station")

    # Statistics
    stats = get_job_statistics()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pending Review", stats['pending'])
    with col2:
        st.metric("Applied", stats['applied'])
    with col3:
        st.metric("Passed On", stats['denied'])
    with col4:
        st.metric("Last 7 Days", stats['recent_7_days'])

    st.divider()

    # Job submission
    st.subheader("Submit New Job")
    with st.form("job_submission"):
        job_url = st.text_input(
            "Job URL",
            placeholder="https://company.com/careers/job-posting",
            help="Paste a job posting URL to analyze"
        )
        submit_btn = st.form_submit_button("🔍 Analyze Job", width='stretch')

        if submit_btn and job_url:
            with st.spinner("Trinity is analyzing the job posting..."):
                result = submit_job_url(job_url)

                if result.get('success'):
                    st.success(f"✅ Job processed! Fit score: {result.get('fit_score', 'N/A')}/100")
                    if result.get('status') == 'accepted':
                        st.info("📝 Draft cover letter created and ready for review!")
                    else:
                        st.warning(f"⚠️ Job rejected: {result.get('reason', 'Unknown')}")
                else:
                    st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

    st.divider()

    # Recent jobs
    st.subheader("Recent Applications")
    jobs = get_recent_jobs(limit=5)

    if jobs:
        for job in jobs:
            with st.expander(f"{job['company']} - {job['position']} ({job['status']})"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Fit Score:** {job['fit_score']}/100")
                    st.write(f"**Created:** {job['created_date']}")
                with col2:
                    status_emoji = {
                        'pending': '⏳',
                        'applied': '✅',
                        'denied': '❌'
                    }.get(job['status'], '❓')
                    st.write(f"**Status:** {status_emoji} {job['status'].title()}")

                if job['draft_filename']:
                    draft_path = DRAFT_DIR / job['draft_filename']
                    if draft_path.exists():
                        if st.button(f"📄 View Draft", key=f"draft_{job['draft_filename']}"):
                            with open(draft_path) as f:
                                st.text_area("Cover Letter", f.read(), height=300)
    else:
        st.info("No jobs yet. Submit a job URL above to get started!")

    # Quick link to full dashboard
    st.divider()
    st.markdown(f"[📊 Open Full Job Dashboard]({TRINITY_API_BASE}/dashboard)")

# ============================================================================
# CAD/ENGINEERING MODULE
# ============================================================================

def generate_scad_code(prompt: str, vr_mode: bool = False) -> str:
    """Generate OpenSCAD code using AI."""
    import google.generativeai as genai

    if not GEMINI_API_KEY:
        return "// Error: GEMINI_API_KEY not set"

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

    system_prompt = f"""You are an OpenSCAD code generator. Generate clean, well-commented OpenSCAD code.

{'VR MODE: Keep models SIMPLE (< 5000 triangles). Use basic shapes. Avoid complex curves.' if vr_mode else 'Generate detailed, production-ready models.'}

Rules:
1. Use parametric design with variables at the top
2. Add comments explaining the design
3. Use proper OpenSCAD syntax
4. Include dimensions in comments
5. Make the code modular and reusable

User Request: {prompt}

Generate ONLY the OpenSCAD code, no explanations before or after."""

    try:
        response = model.generate_content(system_prompt)
        code = response.text

        # Extract code block if wrapped in markdown
        if '```' in code:
            code = code.split('```')[1]
            if code.startswith('openscad\n'):
                code = code[9:]
            elif code.startswith('scad\n'):
                code = code[5:]

        return code.strip()
    except Exception as e:
        return f"// Error generating code: {str(e)}"

def compile_scad_to_stl(scad_code: str, output_name: str, timeout: int = 60) -> Tuple[bool, str, Optional[Path]]:
    """Compile OpenSCAD code to STL file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{timestamp}_{output_name}"

    scad_path = CAD_OUTPUT_DIR / f"{base_name}.scad"
    stl_path = CAD_OUTPUT_DIR / f"{base_name}.stl"

    # Write SCAD file
    with open(scad_path, 'w') as f:
        f.write(scad_code)

    # Check if openscad is installed
    openscad_path = subprocess.run(['which', 'openscad'], capture_output=True, text=True).stdout.strip()
    if not openscad_path:
        return False, "OpenSCAD not installed. Run: brew install --cask openscad", None

    # Compile to STL
    try:
        result = subprocess.run([
            'openscad',
            '-o', str(stl_path),
            str(scad_path)
        ], capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0 and stl_path.exists():
            return True, f"✅ Model compiled successfully!\n\nFiles:\n- {scad_path}\n- {stl_path}", stl_path
        else:
            error_msg = result.stderr if result.stderr else "Unknown compilation error"
            return False, f"❌ Compilation failed:\n{error_msg}", None

    except subprocess.TimeoutExpired:
        return False, f"❌ Compilation timed out after {timeout} seconds. Try simplifying the model.", None
    except Exception as e:
        return False, f"❌ Error: {str(e)}", None

def render_engineering_station():
    """Render the CAD/Engineering module."""
    st.header("🔧 Engineering Station")

    vr_mode = is_vr_mode()
    if vr_mode:
        st.info("🥽 VR Mode Active - Models will be simplified for Quest 1")

    # CAD prompt interface
    st.subheader("3D Model Generator")

    # Examples
    with st.expander("💡 Example Prompts"):
        st.markdown("""
        - "Design a hex bolt M8x20mm"
        - "Create a cable management clip for 1/4 inch cables"
        - "Make a parametric box 100x60x40mm with rounded corners"
        - "Design a door stop wedge"
        - "Create a phone stand with 45 degree angle"
        """)

    with st.form("cad_generation"):
        cad_prompt = st.text_area(
            "Describe what you want to design:",
            height=100,
            placeholder="Example: Design a hex bolt M8x20mm with standard thread pitch"
        )

        col1, col2 = st.columns([3, 1])
        with col1:
            generate_btn = st.form_submit_button("⚙️ Generate Model", width='stretch')
        with col2:
            vr_optimize = st.checkbox("VR Optimize", value=vr_mode)

        if generate_btn and cad_prompt:
            with st.spinner("🤖 Trinity is designing your model..."):
                # Generate OpenSCAD code
                scad_code = generate_scad_code(cad_prompt, vr_optimize)

                # Show generated code
                st.subheader("Generated OpenSCAD Code")
                st.code(scad_code, language='openscad')

                # Compile to STL
                with st.spinner("🔨 Compiling to STL..."):
                    success, message, stl_path = compile_scad_to_stl(
                        scad_code,
                        output_name=cad_prompt[:30].replace(' ', '_'),
                        timeout=30 if vr_optimize else 60
                    )

                    if success:
                        st.success(message)
                        st.session_state.last_cad_render = {
                            'timestamp': datetime.now(),
                            'prompt': cad_prompt,
                            'stl_path': str(stl_path),
                            'scad_code': scad_code
                        }

                        # Download button
                        with open(stl_path, 'rb') as f:
                            st.download_button(
                                "⬇️ Download STL File",
                                f.read(),
                                file_name=stl_path.name,
                                mime="application/octet-stream"
                            )

                        # 3D Preview
                        if not vr_mode:
                            st.info("💡 Tip: Use software like Blender, FreeCAD, or online STL viewers to visualize the model.")
                        else:
                            st.info("🥽 For VR viewing, download the STL and use an Oculus-compatible viewer app.")
                    else:
                        st.error(message)

    st.divider()

    # Recent models
    st.subheader("Recent Models")
    scad_files = sorted(CAD_OUTPUT_DIR.glob("*.scad"), key=os.path.getmtime, reverse=True)[:5]

    if scad_files:
        for scad_file in scad_files:
            stl_file = scad_file.with_suffix('.stl')
            with st.expander(f"📐 {scad_file.stem}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Created:** {datetime.fromtimestamp(scad_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}")
                    if stl_file.exists():
                        st.write(f"**STL Size:** {stl_file.stat().st_size / 1024:.1f} KB")
                with col2:
                    if stl_file.exists():
                        with open(stl_file, 'rb') as f:
                            st.download_button(
                                "⬇️ STL",
                                f.read(),
                                file_name=stl_file.name,
                                key=f"download_{stl_file.stem}"
                            )

                # Show code preview
                with open(scad_file) as f:
                    code_preview = f.read()[:500]
                    st.code(code_preview + "..." if len(code_preview) >= 500 else code_preview, language='openscad')
    else:
        st.info("No models yet. Generate your first model above!")

# ============================================================================
# TRADING BOT MODULE
# ============================================================================

def get_bot_status(pid: int) -> Dict:
    """Check if a bot process is running."""
    try:
        import psutil
        process = psutil.Process(pid)
        return {
            'running': True,
            'cpu_percent': process.cpu_percent(interval=0.1),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'status': process.status()
        }
    except:
        return {'running': False}

def get_phoenix_stats() -> Dict:
    """Get Phoenix trading bot statistics."""
    try:
        if not PHOENIX_LOG.exists():
            return {'error': 'Log file not found'}

        # Read last 100 lines
        with open(PHOENIX_LOG) as f:
            lines = f.readlines()[-100:]

        # Parse latest status
        latest_price = None
        latest_rsi = None
        position = "FLAT"

        for line in reversed(lines):
            if '[INFO]' in line and '$' in line:
                # Format: $628.52 | RSI:33.1 | ATR:0.12 | SMA:HOLD | Pos:FLAT
                parts = line.split('|')
                for part in parts:
                    if '$' in part and not latest_price:
                        latest_price = part.strip().split('$')[1].split()[0]
                    if 'RSI:' in part and not latest_rsi:
                        latest_rsi = part.split('RSI:')[1].strip().split()[0]
                    if 'Pos:' in part:
                        position = part.split('Pos:')[1].strip()
                if latest_price:
                    break

        # Get process status
        phoenix_pids = subprocess.run(
            ['pgrep', '-f', 'mark_xii_phoenix.py'],
            capture_output=True, text=True
        ).stdout.strip().split('\n')

        running = any(pid.strip().isdigit() for pid in phoenix_pids if pid.strip())

        return {
            'running': running,
            'symbol': 'QQQ',
            'latest_price': latest_price,
            'rsi': latest_rsi,
            'position': position,
            'log_updated': datetime.fromtimestamp(PHOENIX_LOG.stat().st_mtime).strftime('%H:%M:%S')
        }
    except Exception as e:
        return {'error': str(e)}

def get_genesis_stats() -> Dict:
    """Get Genesis trading bot statistics."""
    try:
        if not GENESIS_LOG.exists():
            return {'error': 'Log file not found'}

        # Get process status
        genesis_pids = subprocess.run(
            ['pgrep', '-f', 'mark_xi_genesis.py'],
            capture_output=True, text=True
        ).stdout.strip().split('\n')

        running = any(pid.strip().isdigit() for pid in genesis_pids if pid.strip())

        # Read last few lines for status
        with open(GENESIS_LOG) as f:
            lines = f.readlines()[-50:]

        latest_equity = None
        for line in reversed(lines):
            if 'equity' in line.lower() or '$' in line:
                # Try to extract equity value
                import re
                match = re.search(r'\$[\d,]+\.?\d*', line)
                if match:
                    latest_equity = match.group()
                    break

        return {
            'running': running,
            'symbol': 'QQQ',
            'equity': latest_equity or 'Unknown',
            'log_updated': datetime.fromtimestamp(GENESIS_LOG.stat().st_mtime).strftime('%H:%M:%S')
        }
    except Exception as e:
        return {'error': str(e)}

def get_macro_status_data() -> Dict:
    """Get macro trading status."""
    try:
        if not MACRO_STATUS.exists():
            return {'current_action': 'UNKNOWN', 'trading_enabled': None}

        with open(MACRO_STATUS) as f:
            data = json.load(f)

        return {
            'current_action': data.get('current_action', 'UNKNOWN'),
            'trading_enabled': data.get('trading_enabled', None),
            'last_alert': data.get('last_alert', {}).get('alert_name') if data.get('last_alert') else None,
            'last_update': data.get('last_update', 'Never')
        }
    except Exception as e:
        return {'error': str(e)}

def render_trading_station():
    """Render the Trading Bot monitoring module."""
    st.header("📊 Trading Station")

    # Phoenix Mark XII Genesis V2 Champion Badge
    st.success("🏆 **Phoenix Mark XII Genesis V2** - Validated Champion (Feb 3, 2026)")

    with st.expander("📈 Validation Results (5,000 simulations)"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Fitness Score", "121.08")
            st.metric("Sharpe Ratio", "2.14")
            st.metric("Sortino Ratio", "15.46")
        with col2:
            st.metric("Calmar Ratio", "19.40")
            st.metric("Profit Probability", "99.05%")
            st.metric("Median Return", "+103.5%")
        with col3:
            st.metric("Max Drawdown", "8.8%")
            st.metric("Ruin Probability", "0.0%")
            st.write("**Strategy:** QQQ Options (Calls + Puts)")

    st.divider()

    # Macro Status
    macro = get_macro_status_data()
    if 'error' not in macro:
        action_color = {
            'NORMAL_MODE': '🟢',
            'DEFENSIVE_MODE': '🟡',
            'HALT_IMMEDIATELY': '🔴'
        }.get(macro['current_action'], '⚪')

        st.info(f"{action_color} **Macro Status:** {macro['current_action']}")

    st.divider()

    # Phoenix Mark XII Genesis V2 Status (Single Card)
    phoenix = get_phoenix_stats()

    if 'error' in phoenix:
        st.error(f"Error: {phoenix['error']}")
    else:
        # Status indicator
        status_emoji = "🟢" if phoenix['running'] else "🔴"
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Status", f"{status_emoji} {'Online' if phoenix['running'] else 'Offline'}")
        with col2:
            st.write(f"**Last Update:** {phoenix['log_updated']}")

        if phoenix['running']:
            # Live metrics
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Symbol", phoenix['symbol'])
                st.metric("QQQ Price", f"${phoenix['latest_price']}" if phoenix['latest_price'] else "N/A")
            with col_b:
                st.metric("RSI", phoenix['rsi'] if phoenix['rsi'] else "N/A")
                st.metric("Position", phoenix['position'])
            with col_c:
                st.metric("Strategy", "Options")
                st.write("**Type:** Calls + Puts")
        else:
            st.warning("⚠️ Phoenix is offline. Start it with: `python3 mark_xii_phoenix.py`")

    st.divider()

    # Quick Actions
    st.divider()
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📈 View Trading Log", width='stretch'):
            if PHOENIX_LOG.exists():
                with open(PHOENIX_LOG) as f:
                    log_content = f.readlines()[-50:]
                st.text_area("Phoenix Mark XII Genesis V2 Log (Last 50 lines)", "".join(log_content), height=400)
            else:
                st.error("Log file not found")

    with col2:
        if st.button("🔄 Refresh Status", width='stretch'):
            st.rerun()

    # Link to Bot-Factory
    st.divider()
    st.markdown(f"[🤖 Open Bot-Factory Directory](file://{BOT_FACTORY_DIR})")

# ============================================================================
# MAIN COMMAND CENTER INTERFACE
# ============================================================================

def render_header():
    """Render the command center header."""
    st.set_page_config(
        page_title="Trinity Command Center",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for VR mode
    if is_vr_mode():
        st.markdown("""
        <style>
        .main {
            font-size: 1.2em;
        }
        button {
            font-size: 1.2em !important;
            padding: 1em !important;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("🎯 TRINITY COMMAND CENTER")
    st.caption("Unified AI Workstation • Career • Engineering • Trading")

def render_sidebar():
    """Render the sidebar with module selection and settings."""
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1E1E1E/00FF00?text=TRINITY", width='stretch')

        st.header("Control Panel")

        # VR Mode Toggle
        vr_toggle = st.toggle(
            "🥽 VR Mode",
            value=st.session_state.vr_mode,
            help="Optimize interface for Oculus Quest 1"
        )
        if vr_toggle != st.session_state.vr_mode:
            st.session_state.vr_mode = vr_toggle
            st.rerun()

        st.divider()

        # Module Selection
        st.subheader("Stations")
        module = st.radio(
            "Select Module:",
            ["Career", "Engineering", "Trading"],
            index=["Career", "Engineering", "Trading"].index(st.session_state.active_module),
            label_visibility="collapsed"
        )

        if module != st.session_state.active_module:
            st.session_state.active_module = module
            st.rerun()

        st.divider()

        # System Status
        st.subheader("System Status")

        # Check if services are running (by port, not process name)
        trinity_running = subprocess.run(['lsof', '-i', ':8001'], capture_output=True).returncode == 0
        phoenix_running = subprocess.run(['pgrep', '-f', 'mark_xii_phoenix'], capture_output=True).returncode == 0

        st.write("🎯 Trinity API:", "🟢" if trinity_running else "🔴")
        st.write("🏆 Phoenix Mark XII Genesis V2:", "🟢" if phoenix_running else "🔴")

        if phoenix_running:
            st.caption("✅ Champion validated Feb 3, 2026")

        st.divider()

        # Quick Info
        st.caption(f"**Location:** {os.uname().nodename}")
        st.caption(f"**Time:** {datetime.now().strftime('%H:%M:%S')}")

        if st.button("🔄 Refresh", width='stretch'):
            st.rerun()

def main():
    """Main application entry point."""
    initialize_session_state()
    render_header()
    render_sidebar()

    # Route to active module
    if st.session_state.active_module == "Career":
        render_career_station()
    elif st.session_state.active_module == "Engineering":
        render_engineering_station()
    elif st.session_state.active_module == "Trading":
        render_trading_station()

    # Footer
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.caption("Trinity Command Center v1.0 • Powered by Gemini & Claude")

if __name__ == "__main__":
    main()
