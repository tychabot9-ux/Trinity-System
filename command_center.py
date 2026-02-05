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
  🧠 Memory Dashboard - View profile, preferences & insights
  🤖 AI Assistant - Chat with Trinity AI (files, voice, images)
  📊 Trading Station - Bot monitoring & performance
  💼 Business Station - Autonomous income operations

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

# Trinity Memory imports
try:
    from trinity_memory import get_memory, MEMORY_DB
except ImportError:
    MEMORY_DB = Path(__file__).parent / "data" / "trinity_memory.db"

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
JOB_STATUS_DB = BASE_DIR / "job_logs" / "job_status.db"  # Fixed: matches job_status.py
DRAFT_DIR = BASE_DIR / "email_drafts"
CAD_OUTPUT_DIR = BASE_DIR / "cad_output"
CAD_PREVIEWS_DIR = CAD_OUTPUT_DIR / "previews"

# Trading bot paths
PHOENIX_LOG = BOT_FACTORY_DIR / "mark_xii_phoenix.log"
GENESIS_LOG = BOT_FACTORY_DIR / "mark_xi_genesis.log"
MACRO_STATUS = BOT_FACTORY_DIR / "macro_status.json"

# Ensure directories exist
try:
    JOB_STATUS_DB.parent.mkdir(parents=True, exist_ok=True)
    CAD_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CAD_PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create directories: {e}")

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
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'uploaded_files_cache' not in st.session_state:
        st.session_state.uploaded_files_cache = []
    if 'memory_initialized' not in st.session_state:
        st.session_state.memory_initialized = False
        _initialize_trinity_memory()

def _initialize_trinity_memory():
    """Initialize Trinity Memory with user profile."""
    try:
        from trinity_memory import get_memory
        memory = get_memory()

        # Verify memory system is working
        try:
            test_profile = memory.get_profile('system_initialized')
        except Exception as e:
            print(f"Warning: Trinity Memory database error: {e}")
            return

        # Check if profile exists
        existing_profile = memory.get_profile('name')
        if not existing_profile:
            # Initialize user profile
            memory.set_profile('name', 'Ty Brown', 'personal')
            memory.set_profile('email', 'tychabot9@gmail.com', 'personal')
            memory.set_profile('role', 'Developer & Trader', 'professional')
            memory.set_profile('github', 'tychabot9-ux', 'professional')
            memory.set_profile('system_initialized', datetime.now().isoformat(), 'system')
            memory.set_profile('location', os.uname().nodename, 'system')

            # Set initial preferences
            memory.learn_preference('Trading', 'bot', 'active_system', 'Phoenix Mark XII Genesis V2')
            memory.learn_preference('Trading', 'strategy', 'champion_fitness', 121.08)
            memory.learn_preference('Trading', 'risk', 'paper_trading', True)
            memory.learn_preference('Engineering', 'CAD', 'tool', 'OpenSCAD')
            memory.learn_preference('Career', 'job_search', 'active', True)

            # Add initial knowledge
            memory.add_knowledge(
                'Phoenix Bot',
                'Phoenix Mark XII Genesis V2 - Validated champion trading bot. Fitness: 121.08, Sharpe: 2.14, Sortino: 15.46, Profit probability: 99.05%. Completed 320 trades.',
                source='Validation Feb 3, 2026'
            )

            memory.add_knowledge(
                'Trinity System',
                'Personal AI Operating System with Command Center, Career Station, Engineering Station, AI Assistant, and Trading Station. Military-grade personalized intelligence.',
                source='System initialization'
            )

        st.session_state.memory_initialized = True

    except Exception as e:
        print(f"Warning: Trinity Memory initialization failed: {e}")

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

def init_job_status_db():
    """Initialize job status database if it doesn't exist."""
    try:
        JOB_STATUS_DB.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(JOB_STATUS_DB)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_statuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draft_filename TEXT UNIQUE,
                company TEXT NOT NULL,
                position TEXT NOT NULL,
                fit_score INTEGER,
                status TEXT DEFAULT 'pending',
                contact_email TEXT,
                contact_name TEXT,
                contact_phone TEXT,
                job_url TEXT,
                source TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied_date TIMESTAMP,
                response_date TIMESTAMP,
                notes TEXT
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON job_statuses(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_company ON job_statuses(company)")

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Warning: Could not initialize job status database: {e}")
        return False

def get_job_statistics() -> Dict:
    """Get job application statistics from database."""
    try:
        # Ensure database is initialized
        init_job_status_db()

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
        print(f"Error getting job statistics: {e}")
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
        # Ensure database is initialized
        init_job_status_db()

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
        print(f"Error getting recent jobs: {e}")
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
                            try:
                                with open(draft_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    st.text_area("Cover Letter", content, height=300)
                            except Exception as e:
                                st.error(f"Error reading draft: {str(e)}")
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
    try:
        import google.generativeai as genai
    except ImportError:
        return "// Error: google-generativeai package not installed. Install with: pip install google-generativeai"

    if not GEMINI_API_KEY:
        return "// Error: GEMINI_API_KEY not set"

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Use gemini-2.5-flash for better results and faster generation
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        return f"// Error configuring Gemini API: {str(e)}"

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
    try:
        # Ensure output directory exists
        CAD_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize output name to prevent path traversal - strict security
        safe_output_name = "".join(c for c in output_name if c.isalnum() or c in ('_', '-'))

        # Additional security: ensure no path traversal characters remain
        if '..' in safe_output_name or '/' in safe_output_name or '\\' in safe_output_name:
            safe_output_name = safe_output_name.replace('..', '').replace('/', '').replace('\\', '')

        # Limit length to prevent DOS
        safe_output_name = safe_output_name[:50]

        base_name = f"{timestamp}_{safe_output_name}" if safe_output_name else timestamp

        scad_path = CAD_OUTPUT_DIR / f"{base_name}.scad"
        stl_path = CAD_OUTPUT_DIR / f"{base_name}.stl"

        # Final security check: ensure paths are within CAD_OUTPUT_DIR
        if not scad_path.resolve().is_relative_to(CAD_OUTPUT_DIR.resolve()):
            return False, "Security error: Path traversal attempt blocked", None
        if not stl_path.resolve().is_relative_to(CAD_OUTPUT_DIR.resolve()):
            return False, "Security error: Path traversal attempt blocked", None

        # Write SCAD file
        try:
            with open(scad_path, 'w') as f:
                f.write(scad_code)
        except Exception as e:
            return False, f"Error writing SCAD file: {str(e)}", None

        # Check if openscad is installed
        try:
            openscad_path = subprocess.run(['which', 'openscad'], capture_output=True, text=True, timeout=5).stdout.strip()
        except subprocess.TimeoutExpired:
            return False, "Timeout checking for OpenSCAD installation", None

        if not openscad_path:
            return False, "OpenSCAD not installed. Run: brew install --cask openscad", None
    except Exception as e:
        return False, f"Initialization error: {str(e)}", None

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

    # VR Workspace Quick Access
    st.info("🥽 **VR Workspace Available** - Access wireless VR engineering environment")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.link_button("🎮 Open VR Workspace", "http://localhost:8503", use_container_width=True, type="primary")
    with col2:
        st.markdown("""
        **Quest Access URLs:**
        - Tailscale: `100.66.103.8:8503`
        - Local WiFi: `192.168.1.216:8503`
        """)

    st.divider()

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
                try:
                    with open(scad_file, 'r', encoding='utf-8') as f:
                        code_preview = f.read()[:500]
                        st.code(code_preview + "..." if len(code_preview) >= 500 else code_preview, language='openscad')
                except Exception as e:
                    st.caption(f"Could not preview: {str(e)}")
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
        if not BOT_FACTORY_DIR.exists():
            return {'error': f'Bot-Factory directory not found at {BOT_FACTORY_DIR}'}

        if not PHOENIX_LOG.exists():
            return {'error': 'Log file not found', 'path': str(PHOENIX_LOG)}

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
        try:
            phoenix_pids = subprocess.run(
                ['pgrep', '-f', 'mark_xii_phoenix.py'],
                capture_output=True, text=True, timeout=5
            ).stdout.strip().split('\n')

            running = any(pid.strip().isdigit() for pid in phoenix_pids if pid.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            print(f"Warning: Could not check Phoenix process status: {e}")
            running = False

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
        if not BOT_FACTORY_DIR.exists():
            return {'error': f'Bot-Factory directory not found at {BOT_FACTORY_DIR}'}

        if not GENESIS_LOG.exists():
            return {'error': 'Log file not found', 'path': str(GENESIS_LOG)}

        # Get process status
        try:
            genesis_pids = subprocess.run(
                ['pgrep', '-f', 'mark_xi_genesis.py'],
                capture_output=True, text=True, timeout=5
            ).stdout.strip().split('\n')

            running = any(pid.strip().isdigit() for pid in genesis_pids if pid.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            print(f"Warning: Could not check Genesis process status: {e}")
            running = False

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
        if not BOT_FACTORY_DIR.exists():
            return {'error': f'Bot-Factory directory not found at {BOT_FACTORY_DIR}', 'current_action': 'UNKNOWN'}

        if not MACRO_STATUS.exists():
            return {'current_action': 'UNKNOWN', 'trading_enabled': None, 'error': 'macro_status.json not found'}

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

# ============================================================================
# AI ASSISTANT STATION
# ============================================================================

def process_ai_message(user_message: str, uploaded_files: list = None) -> str:
    """Process user message with Trinity AI Assistant."""
    try:
        import google.generativeai as genai
        from trinity_memory import get_memory

        if not GEMINI_API_KEY:
            return "⚠️ Error: GEMINI_API_KEY not configured. Please set your Google API key."

        genai.configure(api_key=GEMINI_API_KEY)

        # Use gemini-2.5-flash for all cases (supports vision, text, and files)
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Get Trinity Memory for enhanced context
        memory = get_memory()

        # Log interaction
        memory.log_interaction('AI Assistant', 'chat_message', {
            'message_length': len(user_message),
            'has_files': bool(uploaded_files)
        })

        # Build conversation context
        conversation_parts = []

        # Add chat history context (last 10 messages for context)
        if st.session_state.chat_history:
            context = "Previous conversation:\n"
            for msg in st.session_state.chat_history[-10:]:
                context += f"{msg['role'].title()}: {msg['content'][:200]}\n"
            conversation_parts.append(context)

        # Get user profile from memory
        user_profile = memory.get_full_profile()
        preferences = memory.get_all_preferences()
        recent_decisions = memory.get_decisions(limit=5)

        # Build enhanced system context with memory
        system_context = f"""You are Trinity, an advanced AI assistant with military-grade personalized intelligence.

USER PROFILE:
{json.dumps(user_profile, indent=2) if user_profile else 'No profile data yet'}

LEARNED PREFERENCES:
{json.dumps(preferences, indent=2) if preferences else 'Learning user preferences...'}

RECENT DECISIONS:
{json.dumps([{'station': d['station'], 'type': d['decision_type'], 'decision': d['decision']} for d in recent_decisions], indent=2) if recent_decisions else 'No recent decisions'}

CAPABILITIES:
- Career Station: Job hunting automation and tracking
- Engineering Station: CAD/3D modeling with OpenSCAD
- Trading Station: Algorithmic trading with Phoenix Mark XII Genesis V2 (validated champion)
- Memory System: Long-term memory, preference learning, decision tracking

INSTRUCTIONS:
- Use the user profile and preferences to provide highly personalized responses
- Reference past decisions and patterns when relevant
- Provide context-aware suggestions based on learned behavior
- Be thorough and insightful when analyzing files
- Always maintain privacy and security of personal data"""
        conversation_parts.append(system_context)

        # Process uploaded files
        if uploaded_files:
            for file in uploaded_files:
                try:
                    # Check file size to prevent memory issues (max 10MB per file)
                    file.seek(0, 2)  # Seek to end
                    file_size = file.tell()
                    file.seek(0)  # Seek back to start

                    if file_size > 10 * 1024 * 1024:  # 10MB
                        conversation_parts.append(f"[File too large: {file.name}, {file_size / 1024 / 1024:.1f}MB - skipped]")
                        continue

                    if file.type and file.type.startswith('image/'):
                        # Handle image files
                        try:
                            import PIL.Image
                            image = PIL.Image.open(file)
                            conversation_parts.append(image)
                            conversation_parts.append(f"[Image: {file.name}]")
                        except Exception as e:
                            conversation_parts.append(f"[Error loading image {file.name}: {str(e)}]")
                    else:
                        # Handle text-based files
                        content = file.read()
                        try:
                            text_content = content.decode('utf-8')
                            # Limit content to 10,000 characters to prevent token overflow
                            if len(text_content) > 10000:
                                conversation_parts.append(f"[File: {file.name} (truncated)]\n{text_content[:10000]}\n... [file truncated]")
                            else:
                                conversation_parts.append(f"[File: {file.name}]\n{text_content}")
                        except UnicodeDecodeError:
                            conversation_parts.append(f"[Binary file: {file.name}, {len(content)} bytes]")
                except Exception as e:
                    conversation_parts.append(f"[Error reading {file.name}: {str(e)}]")

        # Add current user message
        conversation_parts.append(f"User: {user_message}")

        # Generate response
        response = model.generate_content(conversation_parts)
        return response.text

    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"

# ============================================================================
# MEMORY DASHBOARD
# ============================================================================

def render_memory_dashboard():
    """Render Trinity Memory Dashboard - AI-powered memory search."""
    st.header("🧠 Trinity Memory Search")

    st.caption("Ask Trinity about your profile, preferences, decisions, or past interactions")

    try:
        from trinity_memory import get_memory
        import google.generativeai as genai

        memory = get_memory()

        # Quick stats bar
        stats = memory.get_memory_stats()
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Profile", stats['profile_entries'])
        with col2:
            st.metric("Preferences", stats['preferences']['count'])
        with col3:
            st.metric("Decisions", stats['decisions_tracked'])
        with col4:
            st.metric("Interactions", stats['total_interactions'])
        with col5:
            st.metric("Knowledge", stats['knowledge_entries'])

        st.divider()

        # AI-Powered Memory Search
        st.subheader("🔍 Search Your Memory")

        # Initialize session state for memory search history
        if 'memory_search_history' not in st.session_state:
            st.session_state.memory_search_history = []

        # Example queries
        st.caption("**Try asking:**")
        example_col1, example_col2, example_col3 = st.columns(3)
        with example_col1:
            if st.button("💼 My job preferences", width='stretch'):
                search_query = "What are my career and job search preferences?"
                st.session_state.temp_search = search_query
        with example_col2:
            if st.button("📊 Recent decisions", width='stretch'):
                search_query = "Show me my recent decisions from the last week"
                st.session_state.temp_search = search_query
        with example_col3:
            if st.button("🎯 What did I do today?", width='stretch'):
                search_query = "What did I do today?"
                st.session_state.temp_search = search_query

        # Search input
        search_input = st.text_input(
            "Ask about your memory, preferences, decisions, or activities...",
            value=st.session_state.get('temp_search', ''),
            placeholder="e.g., 'What are my CAD preferences?', 'Show decisions from last Tuesday', 'What's my profile?'",
            key="memory_search_input"
        )

        if 'temp_search' in st.session_state:
            del st.session_state.temp_search

        if st.button("🔍 Search Memory", type="primary", width='stretch') and search_input:
            with st.spinner("🧠 Searching Trinity Memory..."):
                # Get comprehensive memory data
                full_profile = memory.get_full_profile()
                all_preferences = memory.get_all_preferences()
                recent_decisions = memory.get_decisions(limit=50)
                interactions = memory.get_interactions(hours=168, limit=500)  # Last week
                insights = memory.get_insights(limit=50)
                knowledge = memory.get_knowledge(limit=100)

                # Build context for AI
                memory_context = f"""
TRINITY MEMORY DATABASE - Query: "{search_input}"

USER PROFILE:
{json.dumps(full_profile, indent=2)}

LEARNED PREFERENCES:
{json.dumps(all_preferences, indent=2)}

RECENT DECISIONS (Last 50):
{json.dumps([{
    'station': d['station'],
    'type': d['decision_type'],
    'decision': d['decision'],
    'context': d.get('context'),
    'timestamp': d['timestamp']
} for d in recent_decisions], indent=2)}

RECENT INTERACTIONS (Last Week):
{json.dumps([{
    'station': i['station'],
    'action': i['action_type'],
    'timestamp': i['timestamp']
} for i in interactions[-100:]], indent=2)}

INSIGHTS:
{json.dumps([{
    'type': i['insight_type'],
    'title': i['title'],
    'confidence': i['confidence']
} for i in insights], indent=2)}

KNOWLEDGE BASE ENTRIES:
{json.dumps([{
    'topic': k['topic'],
    'content': k['content'][:200]
} for k in knowledge[:20]], indent=2)}

MEMORY STATISTICS:
{json.dumps(stats, indent=2)}

TASK:
Answer the user's query based on the Trinity Memory database above. Be specific, cite dates/timestamps when relevant, and provide actionable information. If searching by date, parse the query intelligently (e.g., "last Tuesday", "yesterday", "this week").
"""

                # Generate AI response
                if not GEMINI_API_KEY:
                    st.error("⚠️ GEMINI_API_KEY not configured")
                else:
                    genai.configure(api_key=GEMINI_API_KEY)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(memory_context)

                    # Display results
                    st.success("✅ Search Complete")
                    st.markdown("### 🎯 Results")
                    st.markdown(response.text)

                    # Log the search
                    memory.log_interaction('Memory', 'search', {
                        'query': search_input,
                        'results_length': len(response.text)
                    })

                    # Add to search history
                    st.session_state.memory_search_history.append({
                        'query': search_input,
                        'response': response.text,
                        'timestamp': datetime.now().isoformat()
                    })

        # Recent searches
        if st.session_state.memory_search_history:
            st.divider()
            with st.expander("📜 Recent Searches", expanded=False):
                for search in reversed(st.session_state.memory_search_history[-5:]):
                    st.caption(f"**Q:** {search['query']}")
                    st.caption(f"🕐 {search['timestamp'][:16]}")
                    with st.expander("View Response"):
                        st.markdown(search['response'])
                    st.divider()

        # Quick actions
        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📥 Export Memory", width='stretch'):
                export_data = memory.get_user_summary()
                st.download_button(
                    "💾 Download JSON",
                    json.dumps(export_data, indent=2),
                    file_name=f"trinity_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    width='stretch'
                )

        with col2:
            if st.button("🗑️ Clear Search History", width='stretch'):
                st.session_state.memory_search_history = []
                st.rerun()

    except Exception as e:
        st.error(f"⚠️ Memory system error: {str(e)}")
        st.info("Trinity Memory may not be initialized yet.")

def render_ai_assistant_station():
    """Render the AI Assistant chat interface."""
    st.header("🤖 Trinity AI Assistant")

    st.caption("Chat with Trinity AI • Supports text, images, code, documents, and voice")

    # Chat history display
    chat_container = st.container()

    with chat_container:
        if not st.session_state.chat_history:
            st.info("👋 Hi! I'm Trinity, your AI assistant. Upload files, ask questions, or just chat!")
        else:
            for idx, message in enumerate(st.session_state.chat_history):
                if message['role'] == 'user':
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(message['content'])
                        if 'files' in message and message['files']:
                            st.caption(f"📎 {len(message['files'])} file(s) attached")
                else:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(message['content'])

    # File upload section
    st.divider()
    uploaded_files = st.file_uploader(
        "📎 Upload files (images, PDFs, code, documents)",
        accept_multiple_files=True,
        type=None,  # Accept all file types
        key="ai_file_upload"
    )

    if uploaded_files:
        cols = st.columns(min(len(uploaded_files), 4))
        for idx, file in enumerate(uploaded_files):
            with cols[idx % 4]:
                st.caption(f"📄 {file.name}")
                st.caption(f"{file.type}")

    # Input area
    col1, col2 = st.columns([5, 1])

    with col1:
        user_input = st.chat_input("Type your message here...", key="ai_chat_input")

    with col2:
        # Voice input button (placeholder for future implementation)
        try:
            audio_input = st.audio_input("🎤", key="ai_voice_input")
            if audio_input:
                st.info("🎤 Voice transcription coming soon...")
        except:
            # Fallback if audio_input not available in Streamlit version
            if st.button("🎤 Voice", key="ai_voice_btn", help="Voice input (coming soon)"):
                st.info("🎤 Voice input will be available in future updates")

    # Process user input
    if user_input:
        # Add user message to history
        user_msg = {
            'role': 'user',
            'content': user_input,
            'files': [f.name for f in uploaded_files] if uploaded_files else [],
            'timestamp': datetime.now().isoformat()
        }
        st.session_state.chat_history.append(user_msg)

        # Generate AI response
        with st.spinner("Trinity is thinking..."):
            ai_response = process_ai_message(user_input, uploaded_files)

        # Add AI response to history
        ai_msg = {
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now().isoformat()
        }
        st.session_state.chat_history.append(ai_msg)

        # Rerun to display new messages
        st.rerun()

    # Chat controls
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗑️ Clear Chat", width='stretch'):
            st.session_state.chat_history = []
            st.rerun()

    with col2:
        if st.button("💾 Export Chat", width='stretch'):
            if st.session_state.chat_history:
                export_data = json.dumps(st.session_state.chat_history, indent=2)
                st.download_button(
                    "📥 Download JSON",
                    export_data,
                    file_name=f"trinity_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

    with col3:
        st.caption(f"💬 {len(st.session_state.chat_history)} messages")

def render_business_station():
    """Render the Autonomous Business Dashboard with 30+ Money-Making Services."""
    st.header("💼 Trinity Business Operations")

    st.success("**🚀 30+ Revenue Streams Ready** - Quick wins to premium services")

    # Create business database if it doesn't exist
    business_db = BASE_DIR / "business_data" / "autonomous_business.db"
    business_db.parent.mkdir(parents=True, exist_ok=True)

    try:
        conn = sqlite3.connect(business_db)
        c = conn.cursor()

        # Create tables if they don't exist
        c.execute('''CREATE TABLE IF NOT EXISTS earnings
                    (date TEXT, source TEXT, amount REAL, description TEXT,
                     PRIMARY KEY (date, source, description))''')

        c.execute('''CREATE TABLE IF NOT EXISTS opportunities
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     date_added TEXT, platform TEXT, title TEXT, pay REAL,
                     estimated_hours REAL, capability_match REAL, profitability REAL,
                     risk_level TEXT, status TEXT, notes TEXT)''')

        c.execute('''CREATE TABLE IF NOT EXISTS costs
                    (date TEXT PRIMARY KEY, electricity REAL, internet REAL,
                     api_costs REAL, taxes REAL, total REAL)''')

        # New table: Service catalog with 30+ services
        c.execute('''CREATE TABLE IF NOT EXISTS services
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT UNIQUE,
                     category TEXT,
                     tier TEXT,
                     price_min REAL,
                     price_max REAL,
                     delivery_days REAL,
                     hourly_rate REAL,
                     status TEXT,
                     orders_completed INTEGER DEFAULT 0,
                     revenue_total REAL DEFAULT 0.0,
                     last_order_date TEXT,
                     fiverr_url TEXT,
                     upwork_url TEXT,
                     notes TEXT)''')

        conn.commit()

        # Initialize services catalog (run once)
        c.execute("SELECT COUNT(*) FROM services")
        if c.fetchone()[0] == 0:
            services_data = [
                # TIER 1: QUICK WINS ($25-100, 1-2 days)
                ("QR Code Generation", "Specialized", "Quick Win", 25, 100, 0.5, 300, "Ready to Test"),
                ("3D Model Generation", "3D Modeling", "Quick Win", 50, 300, 1, 150, "Ready to Test"),
                ("Python Automation Script", "Automation", "Quick Win", 75, 150, 1, 100, "Ready to Test"),
                ("Web Scraping Task", "Web Scraping", "Quick Win", 75, 100, 1, 75, "Ready to Test"),

                # TIER 2: MEDIUM PROJECTS ($150-400, 3-5 days)
                ("Streamlit Dashboard", "Dashboards", "Medium", 250, 800, 4, 60, "Ready to Test"),
                ("Social Media Automation Bot", "AI Automation", "Medium", 200, 350, 4, 60, "Ready to Test"),
                ("Job Board Scraper", "Web Scraping", "Medium", 100, 500, 3, 50, "Ready to Test"),
                ("System Health Monitor", "Monitoring", "Medium", 150, 400, 3, 50, "Ready to Test"),
                ("AI Chatbot Integration", "AI Automation", "Medium", 150, 500, 3, 65, "Ready to Test"),
                ("Database Design", "Database", "Medium", 150, 400, 3, 50, "Ready to Test"),
                ("API Development", "Database", "Medium", 300, 1000, 7, 60, "Not Started"),

                # TIER 3: PREMIUM SERVICES ($500-2,000, 1-2 weeks)
                ("Custom Trading Bot", "Trading", "Premium", 800, 2000, 10, 80, "Not Started"),
                ("VR Workspace Development", "3D Modeling", "Premium", 600, 1000, 7, 85, "Ready to Test"),
                ("Full Dashboard Suite", "Dashboards", "Premium", 700, 1200, 10, 70, "Not Started"),
                ("AI Automation Platform", "AI Automation", "Premium", 1000, 2000, 14, 75, "Not Started"),

                # RECURRING REVENUE SERVICES
                ("AI Influencer Automation (Basic)", "AI Automation", "Recurring", 300, 300, 30, 0, "Not Started"),
                ("AI Influencer Automation (Standard)", "AI Automation", "Recurring", 600, 600, 30, 0, "Not Started"),
                ("AI Influencer Automation (Premium)", "AI Automation", "Recurring", 1200, 1200, 30, 0, "Not Started"),

                # ADDITIONAL QUICK SERVICES
                ("Voice AI System", "AI Automation", "Medium", 150, 400, 3, 65, "Ready to Test"),
                ("Trading Signal Dashboard", "Trading", "Medium", 200, 500, 4, 55, "Not Started"),
                ("Portfolio Tracker", "Trading", "Medium", 300, 700, 5, 60, "Not Started"),
                ("VR 3D Content", "3D Modeling", "Medium", 150, 600, 4, 70, "Not Started"),
                ("Custom Web Scraper", "Web Scraping", "Medium", 150, 600, 4, 50, "Not Started"),
                ("Database Optimization", "Database", "Quick Win", 100, 400, 2, 75, "Ready to Test"),
                ("File System Automation", "Automation", "Quick Win", 80, 250, 2, 60, "Ready to Test"),
                ("Mobile Dashboard", "Dashboards", "Medium", 300, 700, 6, 55, "Not Started"),
                ("AI Content Writer", "AI Automation", "Medium", 200, 500, 4, 60, "Not Started"),
                ("Image Generation Integration", "AI Automation", "Medium", 200, 500, 4, 60, "Not Started"),
                ("Clipboard Sync Tool", "Specialized", "Quick Win", 100, 300, 2, 65, "Ready to Test"),
                ("VPN Setup Service", "Specialized", "Medium", 150, 400, 2, 85, "Not Started"),
            ]

            for service in services_data:
                c.execute("""INSERT OR IGNORE INTO services
                           (name, category, tier, price_min, price_max, delivery_days, hourly_rate, status)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", service)
            conn.commit()

        # Calculate totals
        c.execute("SELECT SUM(amount) FROM earnings WHERE date LIKE ?", (datetime.now().strftime('%Y-%m') + '%',))
        monthly_total = c.fetchone()[0] or 0.0

        c.execute("SELECT SUM(amount) FROM earnings WHERE date >= ?",
                 ((datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),))
        quarterly_total = c.fetchone()[0] or 0.0

        c.execute("SELECT SUM(amount) FROM earnings")
        all_time_total = c.fetchone()[0] or 0.0

        c.execute("SELECT SUM(revenue_total) FROM services")
        services_revenue = c.fetchone()[0] or 0.0

        c.execute("SELECT COUNT(*) FROM services WHERE status = 'Launched'")
        launched_count = c.fetchone()[0] or 0

        c.execute("SELECT COUNT(*) FROM services WHERE status = 'Ready to Test'")
        ready_count = c.fetchone()[0] or 0

        # Dashboard metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Monthly Revenue", f"${monthly_total:,.0f}")
        with col2:
            st.metric("📈 Services Revenue", f"${services_revenue:,.0f}")
        with col3:
            st.metric("🚀 Launched", f"{launched_count}/30")
        with col4:
            st.metric("✅ Ready to Test", f"{ready_count}")

        st.divider()

        # Tab navigation for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Service Catalog", "💵 Revenue Tracking", "🎯 Quick Launch", "📋 Opportunities"])

        with tab1:
            st.subheader("🛍️ Complete Service Catalog (30+ Services)")

            # Filter by tier
            tier_filter = st.selectbox("Filter by Tier", ["All", "Quick Win", "Medium", "Premium", "Recurring"])

            # Get services
            if tier_filter == "All":
                c.execute("""SELECT name, category, tier, price_min, price_max, delivery_days,
                           hourly_rate, status, orders_completed, revenue_total
                           FROM services ORDER BY tier, category, name""")
            else:
                c.execute("""SELECT name, category, tier, price_min, price_max, delivery_days,
                           hourly_rate, status, orders_completed, revenue_total
                           FROM services WHERE tier = ? ORDER BY category, name""", (tier_filter,))

            services = c.fetchall()

            if services:
                for service in services:
                    name, category, tier, price_min, price_max, days, hourly, status, orders, revenue = service

                    # Status color
                    status_colors = {
                        "Not Started": "🔴",
                        "Ready to Test": "🟡",
                        "Testing": "🟠",
                        "Launched": "🟢"
                    }
                    status_emoji = status_colors.get(status, "⚪")

                    with st.expander(f"{status_emoji} {name} - ${price_min}-{price_max}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.caption("**Category:**")
                            st.write(category)
                            st.caption("**Tier:**")
                            st.write(tier)
                        with col2:
                            st.caption("**Pricing:**")
                            st.write(f"${price_min}-${price_max}")
                            st.caption("**Delivery:**")
                            st.write(f"{days} days")
                        with col3:
                            st.caption("**Hourly Rate:**")
                            st.write(f"${hourly}/hr")
                            st.caption("**Status:**")
                            st.write(status)

                        if orders > 0:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Orders Completed", orders)
                            with col2:
                                st.metric("Total Revenue", f"${revenue:,.0f}")

                        # Quick actions
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if status == "Not Started":
                                if st.button("🧪 Mark Ready to Test", key=f"ready_{name}"):
                                    c.execute("UPDATE services SET status = 'Ready to Test' WHERE name = ?", (name,))
                                    conn.commit()
                                    st.rerun()
                        with col2:
                            if status == "Ready to Test":
                                if st.button("🚀 Mark as Launched", key=f"launch_{name}"):
                                    c.execute("UPDATE services SET status = 'Launched' WHERE name = ?", (name,))
                                    conn.commit()
                                    st.success(f"Launched {name}!")
                                    st.rerun()
                        with col3:
                            if status == "Launched":
                                if st.button("➕ Add Order", key=f"order_{name}"):
                                    st.session_state[f'adding_order_{name}'] = True
                                    st.rerun()

                        # Add order form
                        if st.session_state.get(f'adding_order_{name}', False):
                            with st.form(key=f"order_form_{name}"):
                                order_amount = st.number_input("Order Amount ($)", min_value=0.0, value=float(price_min))
                                order_notes = st.text_input("Notes (optional)")
                                submitted = st.form_submit_button("Submit Order")
                                if submitted:
                                    # Update service stats
                                    c.execute("""UPDATE services
                                               SET orders_completed = orders_completed + 1,
                                                   revenue_total = revenue_total + ?,
                                                   last_order_date = ?
                                               WHERE name = ?""",
                                             (order_amount, datetime.now().strftime('%Y-%m-%d'), name))
                                    # Add to earnings
                                    c.execute("""INSERT INTO earnings VALUES (?, ?, ?, ?)""",
                                             (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                              name, order_amount, order_notes or "Order completed"))
                                    conn.commit()
                                    st.session_state[f'adding_order_{name}'] = False
                                    st.success(f"Order recorded: ${order_amount}")
                                    st.rerun()
            else:
                st.info("No services found")

        with tab2:
            st.subheader("💵 Revenue Analytics")

            # Overall stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("All-Time Revenue", f"${all_time_total:,.0f}")
            with col2:
                st.metric("This Quarter", f"${quarterly_total:,.0f}")
            with col3:
                target_progress = (all_time_total / 100000.0) * 100
                st.metric("To $100k Goal", f"{target_progress:.1f}%")

            st.divider()

            # Revenue by category
            c.execute("""SELECT category, SUM(revenue_total) as total
                       FROM services GROUP BY category ORDER BY total DESC""")
            cat_revenue = c.fetchall()

            if cat_revenue:
                st.caption("**Revenue by Category:**")
                for cat, total in cat_revenue:
                    if total > 0:
                        st.write(f"**{cat}:** ${total:,.0f}")

            st.divider()

            # Top performers
            c.execute("""SELECT name, orders_completed, revenue_total
                       FROM services WHERE orders_completed > 0
                       ORDER BY revenue_total DESC LIMIT 5""")
            top_services = c.fetchall()

            if top_services:
                st.caption("**Top 5 Services:**")
                for svc_name, orders, rev in top_services:
                    st.write(f"**{svc_name}:** {orders} orders, ${rev:,.0f}")

        with tab3:
            st.subheader("🎯 Quick Launch Services")
            st.info("**These 3 services are tested and ready to launch THIS WEEK**")

            quick_wins = [
                ("QR Code Generation", 25, "10 min", 300),
                ("3D Model Generation", 50, "30 min", 150),
                ("Python Automation Script", 75, "1 hour", 100)
            ]

            for service_name, price, time, hourly in quick_wins:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                    with col1:
                        st.write(f"**{service_name}**")
                    with col2:
                        st.write(f"${price}")
                    with col3:
                        st.write(time)
                    with col4:
                        st.write(f"${hourly}/hr effective")

            st.divider()

            st.markdown("""
            ### 📋 Launch Checklist:

            **Week 1 (This Week):**
            - [ ] Test QR codes (3 hours) - See CAPABILITY_TESTING_CHECKLIST.md
            - [ ] Test 3D models (4 hours)
            - [ ] Test Python scripts (5 hours)

            **Week 2:**
            - [ ] Create Fiverr gigs (Friday)
            - [ ] Set competitive pricing
            - [ ] Upload portfolio screenshots

            **Week 3:**
            - [ ] Deliver first 5-10 orders
            - [ ] Get 5-star reviews
            - [ ] Target: $500-1,000 revenue
            """)

            if st.button("📄 Open Full Testing Checklist", use_container_width=True):
                try:
                    with open(BASE_DIR / "CAPABILITY_TESTING_CHECKLIST.md", 'r') as f:
                        st.text_area("Testing Checklist", f.read(), height=400)
                except:
                    st.error("Testing checklist not found")

        with tab4:
            st.subheader("🔍 Opportunity Queue")

            c.execute("SELECT COUNT(*) FROM opportunities WHERE status = 'pending'")
            pending_count = c.fetchone()[0] or 0

            if pending_count > 0:
                st.info(f"**{pending_count} opportunities** awaiting review")

                # Show opportunities
                c.execute("""SELECT id, platform, title, pay, estimated_hours,
                            capability_match, profitability, risk_level
                            FROM opportunities WHERE status = 'pending'
                            ORDER BY profitability DESC LIMIT 5""")
                opportunities = c.fetchall()

                for opp in opportunities:
                    opp_id, platform, title, pay, hours, match, profit, risk = opp

                    with st.expander(f"💼 {title} - ${pay:,.0f}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Platform", platform)
                            st.metric("Pay", f"${pay:,.0f}")
                        with col2:
                            st.metric("Est. Hours", f"{hours:.1f}h")
                            st.metric("Match", f"{match:.0%}")
                        with col3:
                            st.metric("Profitability", f"${profit:,.0f}")
                            st.metric("Risk", risk)

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("✅ Accept", key=f"accept_{opp_id}"):
                                c.execute("UPDATE opportunities SET status = 'accepted' WHERE id = ?", (opp_id,))
                                conn.commit()
                                st.success("Opportunity accepted!")
                                st.rerun()
                        with col2:
                            if st.button("❌ Decline", key=f"decline_{opp_id}"):
                                c.execute("UPDATE opportunities SET status = 'declined' WHERE id = ?", (opp_id,))
                                conn.commit()
                                st.info("Opportunity declined")
                                st.rerun()
                        with col3:
                            if st.button("📝 Review Later", key=f"later_{opp_id}"):
                                st.info("Will review later")
            else:
                st.info("No pending opportunities. Autonomous monitoring active.")

        st.divider()

        # Recent Activity
        st.subheader("📋 Recent Activity & Earnings Log")

        c.execute("""SELECT date, source, amount, description
                    FROM earnings ORDER BY date DESC LIMIT 15""")
        recent_earnings = c.fetchall()

        if recent_earnings:
            for date, source, amount, desc in recent_earnings:
                col1, col2, col3 = st.columns([2, 2, 3])
                with col1:
                    st.caption(date[:16])
                with col2:
                    st.caption(source)
                with col3:
                    st.caption(f"**${amount:.2f}** - {desc}")
        else:
            st.caption("No earnings yet. Launch quick win services to start earning!")

        st.divider()

        # Planning Documents
        st.subheader("📚 Strategic Planning Documents")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📄 Master Decade Plan", use_container_width=True):
                try:
                    with open(BASE_DIR / "MASTER_DECADE_PLAN_MONTHLY.md", 'r') as f:
                        content = f.read()
                        st.text_area("Master Decade Plan (120-month roadmap)", content[:5000] + "\n\n...(truncated, see file for full plan)", height=400)
                except:
                    st.error("Master plan not found")

            if st.button("🧪 Testing Checklist", use_container_width=True):
                try:
                    with open(BASE_DIR / "CAPABILITY_TESTING_CHECKLIST.md", 'r') as f:
                        content = f.read()
                        st.text_area("Pre-Launch Testing Checklist", content[:5000] + "\n\n...(truncated, see file for full checklist)", height=400)
                except:
                    st.error("Testing checklist not found")

        with col2:
            if st.button("💰 Money-Making Guide", use_container_width=True):
                try:
                    with open(BASE_DIR / "TRINITY_MONEY_MAKING_CAPABILITIES.md", 'r') as f:
                        content = f.read()
                        st.text_area("30+ Money-Making Services", content[:5000] + "\n\n...(truncated, see file for complete guide)", height=400)
                except:
                    st.error("Money-making guide not found")

            if st.button("🚀 Optimization Strategies", use_container_width=True):
                try:
                    with open(BASE_DIR / "WEALTH_OPTIMIZATION_STRATEGIES.md", 'r') as f:
                        content = f.read()
                        st.text_area("10 Optimization Levers", content[:5000] + "\n\n...(truncated, see file for full strategies)", height=400)
                except:
                    st.error("Optimization strategies not found")

        with col3:
            if st.button("📈 Trading Flywheel Plan", use_container_width=True):
                try:
                    with open(BASE_DIR / "DECADE_PLAN_WITH_FLYWHEEL.md", 'r') as f:
                        content = f.read()
                        st.text_area("Genesis V2 Flywheel Integration", content[:5000] + "\n\n...(truncated, see file for full plan)", height=400)
                except:
                    st.error("Flywheel plan not found")

            if st.button("📊 Export All Data", use_container_width=True):
                # Export all business data
                c.execute("SELECT * FROM services")
                services_data = c.fetchall()
                c.execute("SELECT * FROM earnings")
                earnings_data = c.fetchall()

                export = {
                    "services": [{
                        "name": s[1], "category": s[2], "tier": s[3],
                        "price": f"${s[4]}-${s[5]}", "status": s[8],
                        "orders": s[9], "revenue": s[10]
                    } for s in services_data],
                    "earnings": [{
                        "date": e[0], "source": e[1],
                        "amount": e[2], "description": e[3]
                    } for e in earnings_data],
                    "summary": {
                        "total_revenue": all_time_total,
                        "monthly_revenue": monthly_total,
                        "launched_services": launched_count,
                        "ready_to_test": ready_count
                    }
                }
                st.json(export)

        st.divider()

        # Quick Stats Summary
        st.subheader("📊 Quick Stats")

        col1, col2, col3, col4 = st.columns(4)

        c.execute("SELECT COUNT(*) FROM services WHERE tier = 'Quick Win'")
        quick_win_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM services WHERE tier = 'Medium'")
        medium_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM services WHERE tier = 'Premium'")
        premium_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM services WHERE tier = 'Recurring'")
        recurring_count = c.fetchone()[0]

        with col1:
            st.metric("Quick Wins", f"{quick_win_count} services")
            st.caption("$25-100, 1-2 days")
        with col2:
            st.metric("Medium", f"{medium_count} services")
            st.caption("$150-400, 3-5 days")
        with col3:
            st.metric("Premium", f"{premium_count} services")
            st.caption("$500-2k, 1-2 weeks")
        with col4:
            st.metric("Recurring", f"{recurring_count} services")
            st.caption("$300-1.2k/month")

        conn.close()

    except Exception as e:
        st.error(f"⚠️ Business dashboard error: {str(e)}")
        st.info("Business database will be initialized on first use.")

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
            try:
                if PHOENIX_LOG.exists():
                    with open(PHOENIX_LOG, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.readlines()[-50:]
                    st.text_area("Phoenix Mark XII Genesis V2 Log (Last 50 lines)", "".join(log_content), height=400)
                else:
                    st.error(f"Log file not found at {PHOENIX_LOG}")
            except Exception as e:
                st.error(f"Error reading log file: {str(e)}")

    with col2:
        if st.button("🔄 Refresh Status", width='stretch'):
            st.rerun()

    # Link to Bot-Factory
    st.divider()
    col1, col2 = st.columns([2, 1])
    with col1:
        st.caption("📁 Bot-Factory Directory")
    with col2:
        if st.button("🤖 Open", key="open_bot_factory", width='stretch'):
            try:
                if BOT_FACTORY_DIR.exists():
                    subprocess.run(["open", str(BOT_FACTORY_DIR)], timeout=5)
                    st.success("Opening Bot-Factory...")
                else:
                    st.error(f"Bot-Factory directory not found at {BOT_FACTORY_DIR}")
            except Exception as e:
                st.error(f"Could not open Bot-Factory: {str(e)}")

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

    # Custom CSS styling
    vr_size = "1.3em" if is_vr_mode() else "1em"
    st.markdown(f"""
    <style>
        /* Enhanced UI Styling */
        .main {{
            font-size: {vr_size};
        }}
        button {{
            font-size: {vr_size} !important;
            padding: {'1em' if is_vr_mode() else '0.5em'} !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
        }}
        button:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(0,255,0,0.3) !important;
        }}
        .stChatMessage {{
            border-radius: 10px;
            padding: 1em;
            margin: 0.5em 0;
        }}
        .stTextInput input {{
            border-radius: 8px;
        }}
        .stSelectbox {{
            border-radius: 8px;
        }}
        /* Success/Error styling */
        .stSuccess {{
            border-left: 4px solid #00ff00;
        }}
        .stError {{
            border-left: 4px solid #ff0000;
        }}
        .stInfo {{
            border-left: 4px solid #0088ff;
        }}
        /* Metrics enhancement */
        [data-testid="stMetricValue"] {{
            font-size: 2em;
            font-weight: bold;
            color: #00ff00;
        }}
    </style>
    """, unsafe_allow_html=True)

    st.title("🎯 TRINITY COMMAND CENTER")
    st.caption("Unified AI Workstation • Career • Engineering • Business • Trading")

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
            ["Career", "Engineering", "Memory", "AI Assistant", "Trading", "Business"],
            index=["Career", "Engineering", "Memory", "AI Assistant", "Trading", "Business"].index(st.session_state.active_module),
            label_visibility="collapsed"
        )

        if module != st.session_state.active_module:
            st.session_state.active_module = module
            st.rerun()

        st.divider()

        # System Status
        st.subheader("System Status")

        # Check if services are running (by port, not process name)
        try:
            trinity_running = subprocess.run(['lsof', '-i', ':8001'], capture_output=True, timeout=5).returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            trinity_running = False

        try:
            phoenix_running = subprocess.run(['pgrep', '-f', 'mark_xii_phoenix'], capture_output=True, timeout=5).returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            phoenix_running = False

        st.write("🎯 Trinity API:", "🟢" if trinity_running else "🔴")
        st.write("🏆 Phoenix Mark XII Genesis V2:", "🟢" if phoenix_running else "🔴")

        if phoenix_running:
            st.caption("✅ Champion validated Feb 3, 2026")

        st.divider()

        # Quick Stats
        st.subheader("Quick Stats")
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("CPU", f"{cpu_percent:.0f}%")
            with col2:
                st.metric("RAM", f"{mem.percent:.0f}%")
        except:
            st.caption("📊 Stats unavailable")

        st.divider()

        # Quick Info
        st.caption(f"**Location:** {os.uname().nodename}")
        st.caption(f"**Time:** {datetime.now().strftime('%H:%M:%S')}")

        # Session info
        if st.session_state.chat_history:
            st.caption(f"💬 Chat messages: {len(st.session_state.chat_history)}")

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
    elif st.session_state.active_module == "Memory":
        render_memory_dashboard()
    elif st.session_state.active_module == "AI Assistant":
        render_ai_assistant_station()
    elif st.session_state.active_module == "Trading":
        render_trading_station()
    elif st.session_state.active_module == "Business":
        render_business_station()

    # Footer
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.caption("⚡ Trinity v1.0")
    with col2:
        st.caption("🤖 Gemini + Claude")
    with col3:
        uptime_start = datetime.now() - timedelta(seconds=time.time() % 86400)
        st.caption(f"⏱️ Session: {(datetime.now() - uptime_start).seconds // 60}m")
    with col4:
        with st.popover("⌨️ Shortcuts"):
            st.caption("**Ctrl+K**: Jump to module")
            st.caption("**Ctrl+R**: Refresh")
            st.caption("**Ctrl+/**: Help")

if __name__ == "__main__":
    main()
