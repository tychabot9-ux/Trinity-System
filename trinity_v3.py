#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════╗
║           TRINITY COMMAND CENTER v2.1                          ║
║     Professional AI Workstation with Trinity Personality       ║
║                   Apple Aesthetic • 5 Hubs                     ║
╚════════════════════════════════════════════════════════════════╝

Features:
  📊 Dashboard - System overview
  💰 Financial Hub - Projections + Flywheel + AGRO + Week 1
  🏢 Operations - Career + Business
  🔧 Engineering - CAD/3D modeling  
  🤖 AI Hub - Assistant + Memory + Code
  
  + Trinity AI (Cortana) - Always available in sidebar
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3

import streamlit as st
from dotenv import load_dotenv

# Import Trinity personality
try:
    from trinity_personality import (
        get_trinity_response,
        get_trinity_quick_actions,
        TRINITY_PERSONALITY
    )
    TRINITY_AVAILABLE = True
except ImportError:
    TRINITY_AVAILABLE = False
    print("Warning: Trinity personality not available")

load_dotenv()

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent
BOT_FACTORY_DIR = BASE_DIR.parent / "Bot-Factory"

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# File paths
PHOENIX_LOG = BOT_FACTORY_DIR / "mark_xii_phoenix.log"
OPTIMIZATION_REPORT = BASE_DIR / "TRINITY_OPTIMIZATION_REPORT.md"
FLYWHEEL_PLAN = BASE_DIR / "DECADE_PLAN_WITH_FLYWHEEL.md"

# ═══════════════════════════════════════════════════════════════
# APPLE AESTHETIC STYLING
# ═══════════════════════════════════════════════════════════════

APPLE_STYLE = """
<style>
    /* Apple Store Dark Mode */
    :root {
        --apple-bg: #000000;
        --apple-card: #1c1c1e;
        --apple-card-hover: #2c2c2e;
        --apple-primary: #0a84ff;
        --apple-success: #30d158;
        --apple-warning: #ff9f0a;
        --apple-danger: #ff453a;
        --apple-text: #ffffff;
        --apple-text-secondary: #98989d;
        --apple-border: #38383a;
    }
    
    /* Global Styles */
    .main {
        background-color: var(--apple-bg);
        color: var(--apple-text);
    }
    
    /* Cards with frosted glass effect */
    .stCard, [data-testid="stVerticalBlock"] > div {
        background: var(--apple-card);
        border: 1px solid var(--apple-border);
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stCard:hover {
        background: var(--apple-card-hover);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    
    /* Buttons - Apple style */
    .stButton > button {
        background: var(--apple-primary);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
        font-size: 1rem;
    }
    
    .stButton > button:hover {
        background: #0070e0;
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(10,132,255,0.3);
    }
    
    /* Metrics - Large, bold numbers */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--apple-primary);
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--apple-text);
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    h1 { font-size: 2.5rem; }
    h2 { font-size: 2rem; }
    h3 { font-size: 1.5rem; }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1c1c1e 0%, #000000 100%);
        border-right: 1px solid var(--apple-border);
        padding: 1rem 0.5rem;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: var(--apple-text);
    }

    /* Sidebar Radio Buttons - Custom Navigation Cards */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.5rem;
    }

    [data-testid="stSidebar"] .stRadio > div > label {
        background: rgba(28, 28, 30, 0.6);
        border: 1px solid var(--apple-border);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        backdrop-filter: blur(10px);
    }

    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(44, 44, 46, 0.8);
        border-color: var(--apple-primary);
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(10,132,255,0.2);
    }

    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background: linear-gradient(135deg, rgba(10,132,255,0.2) 0%, rgba(10,132,255,0.05) 100%);
        border-color: var(--apple-primary);
        box-shadow: 0 4px 16px rgba(10,132,255,0.3);
        transform: translateX(4px);
    }

    [data-testid="stSidebar"] .stRadio > div > label > div {
        color: var(--apple-text);
        font-weight: 500;
        font-size: 0.95rem;
    }

    /* Trinity Section Styling */
    .trinity-section {
        background: linear-gradient(135deg, rgba(10,132,255,0.1) 0%, rgba(10,132,255,0.02) 100%);
        border: 1px solid rgba(10,132,255,0.3);
        border-radius: 16px;
        padding: 1rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }

    .trinity-avatar-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 0.5rem;
        margin: 0.5rem 0;
    }

    /* Sidebar Buttons Enhancement */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: rgba(10,132,255,0.15);
        border: 1px solid rgba(10,132,255,0.3);
        padding: 0.6rem 1rem;
        font-size: 0.875rem;
        margin: 0.25rem 0;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(10,132,255,0.25);
        border-color: var(--apple-primary);
        transform: scale(1.02);
    }

    /* Sidebar Text Input */
    [data-testid="stSidebar"] .stTextInput > div > div {
        background: rgba(28,28,30,0.8);
        border: 1px solid var(--apple-border);
        border-radius: 10px;
        transition: all 0.3s ease;
    }

    [data-testid="stSidebar"] .stTextInput > div > div:focus-within {
        border-color: var(--apple-primary);
        box-shadow: 0 0 0 3px rgba(10,132,255,0.2);
    }

    /* Sidebar Caption/Footer */
    [data-testid="stSidebar"] .stCaption {
        color: var(--apple-text-secondary);
        text-align: center;
        font-size: 0.75rem;
        opacity: 0.7;
    }

    /* Status Indicator */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
        animation: pulse 2s infinite;
    }

    .status-online {
        background: var(--apple-success);
        box-shadow: 0 0 8px var(--apple-success);
    }

    .status-offline {
        background: var(--apple-text-secondary);
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Tabs - Apple style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
        border-bottom: 1px solid var(--apple-border);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        color: var(--apple-text-secondary);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--apple-text);
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--apple-primary);
        background: rgba(10,132,255,0.1);
        border-radius: 8px;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: var(--apple-primary);
        border-radius: 8px;
    }
    
    /* Trinity AI Widget */
    .trinity-widget {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(135deg, #1c1c1e 0%, #2c2c2e 100%);
        border: 2px solid var(--apple-primary);
        border-radius: 20px;
        padding: 1rem;
        box-shadow: 0 8px 32px rgba(10,132,255,0.3);
        backdrop-filter: blur(10px);
        z-index: 9999;
        max-width: 80px;
        transition: all 0.3s ease;
    }
    
    .trinity-widget:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 48px rgba(10,132,255,0.5);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--apple-card);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid var(--apple-border);
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--apple-card-hover);
        border-color: var(--apple-primary);
    }
    
    /* Success/Warning/Error colors */
    .stSuccess {
        background: rgba(48,209,88,0.1);
        border-left: 4px solid var(--apple-success);
        border-radius: 8px;
    }
    
    .stWarning {
        background: rgba(255,159,10,0.1);
        border-left: 4px solid var(--apple-warning);
        border-radius: 8px;
    }
    
    .stError {
        background: rgba(255,69,58,0.1);
        border-left: 4px solid var(--apple-danger);
        border-radius: 8px;
    }
    
    .stInfo {
        background: rgba(10,132,255,0.1);
        border-left: 4px solid var(--apple-primary);
        border-radius: 8px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--apple-bg);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--apple-border);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--apple-primary);
    }

    /* Sidebar Dividers */
    [data-testid="stSidebar"] hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, var(--apple-border) 50%, transparent 100%);
        margin: 1rem 0;
    }

    /* Input Focus States */
    input:focus, textarea:focus {
        outline: none;
        border-color: var(--apple-primary) !important;
        box-shadow: 0 0 0 3px rgba(10,132,255,0.2) !important;
    }

    /* Selection Color */
    ::selection {
        background: rgba(10,132,255,0.3);
        color: var(--apple-text);
    }

    /* Smooth Animations */
    * {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* Card Grid Layout */
    [data-testid="column"] {
        gap: 1rem;
    }

    /* Enhanced Shadows for Depth */
    .stCard, [data-testid="stVerticalBlock"] > div:hover {
        box-shadow:
            0 1px 2px rgba(0,0,0,0.1),
            0 2px 4px rgba(0,0,0,0.1),
            0 4px 8px rgba(0,0,0,0.1),
            0 8px 16px rgba(0,0,0,0.1);
    }

    /* Loading Spinner */
    [data-testid="stSpinner"] > div {
        border-color: var(--apple-primary) transparent transparent transparent !important;
    }

    /* Toast Notifications */
    .stToast {
        background: var(--apple-card) !important;
        border: 1px solid var(--apple-border) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
    }
</style>
"""

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════

def init_session():
    """Initialize session state."""
    defaults = {
        'station': 'Dashboard',
        'trinity_chat_history': [],
        'trinity_expanded': False,
        'week1_checklist': {},
        'phoenix_status': None,
        'last_refresh': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def check_phoenix() -> bool:
    """Check if Phoenix is running."""
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'mark_xii_phoenix'],
            capture_output=True,
            timeout=3
        )
        return result.returncode == 0
    except:
        return False

def get_context() -> dict:
    """Get current system context for Trinity."""
    return {
        'burn_rate': -635,
        'phoenix_running': check_phoenix(),
        'week1_done': sum(1 for v in st.session_state.week1_checklist.values() if v),
        'week1_total': 18,
        'quick_cash_ready': 3,
        'trading_capital': 40000
    }

# ═══════════════════════════════════════════════════════════════
# TRINITY AI SIDEBAR
# ═══════════════════════════════════════════════════════════════

def render_trinity_sidebar():
    """Render Trinity AI in sidebar - always available."""
    if not TRINITY_AVAILABLE:
        st.sidebar.markdown("---")
        st.sidebar.warning("⚠️ Trinity AI offline")
        return

    with st.sidebar:
        st.markdown("---")

        # Trinity Section Container
        st.markdown('<div class="trinity-section">', unsafe_allow_html=True)

        # Header with status
        phoenix_status = check_phoenix()
        status_class = "status-online" if phoenix_status else "status-offline"
        status_text = "ONLINE" if phoenix_status else "STANDBY"

        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🤖</div>
            <h3 style="margin: 0; font-size: 1.1rem; font-weight: 600;">
                <span class="status-indicator {status_class}"></span>
                TRINITY AI
            </h3>
            <p style="margin: 0.25rem 0 0 0; font-size: 0.7rem; color: var(--apple-text-secondary); text-transform: uppercase; letter-spacing: 1px;">
                {status_text}
            </p>
            <p style="text-align: center; font-size: 0.8rem; color: var(--apple-text-secondary); margin: 0.5rem 0;">Strategic Advisor</p>
        </div>
        """, unsafe_allow_html=True)

        # Chat Toggle Button
        toggle_text = "▼ Hide Panel" if st.session_state.trinity_expanded else "▲ Open Panel"
        if st.button(f"💬 {toggle_text}", use_container_width=True, key="trinity_toggle"):
            st.session_state.trinity_expanded = not st.session_state.trinity_expanded
            st.rerun()

        # Expanded Panel
        if st.session_state.trinity_expanded:
            st.markdown("---")

            # Quick Actions
            st.markdown("**⚡ Quick Actions**")
            actions = get_trinity_quick_actions()

            # Show actions in compact layout
            for action in actions[:4]:  # Show first 4
                if st.button(action['label'], key=f"trinity_{action['label']}", use_container_width=True):
                    with st.spinner("🔮 Trinity analyzing..."):
                        context = get_context()
                        response = get_trinity_response(action['command'], context)
                        st.session_state.trinity_chat_history.append({
                            'user': action['command'],
                            'trinity': response,
                            'timestamp': datetime.now().strftime('%H:%M')
                        })
                        st.rerun()

            st.markdown("---")

            # Chat interface
            user_input = st.text_input("💭 Ask Trinity", key="trinity_input", placeholder="Type your question...")
            if user_input:
                with st.spinner("🔮 Trinity analyzing..."):
                    context = get_context()
                    response = get_trinity_response(user_input, context)
                    st.session_state.trinity_chat_history.append({
                        'user': user_input,
                        'trinity': response,
                        'timestamp': datetime.now().strftime('%H:%M')
                    })
                    st.rerun()

            # Show recent chat (most recent first)
            if st.session_state.trinity_chat_history:
                st.markdown("---")
                st.markdown("**💬 Recent Conversation**")
                for msg in reversed(st.session_state.trinity_chat_history[-3:]):
                    with st.expander(f"🗨️ {msg['user'][:25]}... • {msg.get('timestamp', '')}"):
                        st.markdown(f"**Trinity:** {msg['trinity']}")

        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# STATIONS
# ═══════════════════════════════════════════════════════════════

def render_dashboard():
    """Dashboard - System overview."""
    st.title("📊 Trinity Dashboard")
    
    # System metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        phoenix_running = check_phoenix()
        st.metric("Phoenix AGRO", "🟢 Active" if phoenix_running else "🔴 Offline")
        
    with col2:
        st.metric("Burn Rate", "-$635/mo", delta="-$330 target")
        
    with col3:
        st.metric("Quick Cash", "3/3 Ready")
        
    with col4:
        week1_done = sum(1 for v in st.session_state.week1_checklist.values() if v)
        st.metric("Week 1", f"{week1_done}/18")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💰 Financial Hub", use_container_width=True):
            st.session_state.station = "Financial Hub"
            st.rerun()
        if st.button("🏢 Operations", use_container_width=True):
            st.session_state.station = "Operations"
            st.rerun()
            
    with col2:
        if st.button("🔧 Engineering", use_container_width=True):
            st.session_state.station = "Engineering"
            st.rerun()
        if st.button("🤖 AI Hub", use_container_width=True):
            st.session_state.station = "AI Hub"
            st.rerun()
            
    with col3:
        if st.button("📊 Phoenix Log", use_container_width=True):
            if PHOENIX_LOG.exists():
                with open(PHOENIX_LOG) as f:
                    st.text_area("Recent Activity", "".join(f.readlines()[-30:]), height=200)
        if st.button("🔄 Refresh All", use_container_width=True):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
    
    # Critical alerts
    st.markdown("---")
    st.subheader("🚨 Critical Alerts")
    
    if not check_phoenix():
        st.error("**Phoenix AGRO Offline** - Start with: `python3 mark_xii_phoenix.py`")
    
    st.warning("**Cash Flow Crisis** - Burn rate: -$635/mo. Execute Week 1 actions immediately.")
    
    # Today's focus
    st.markdown("---")
    st.subheader("🎯 Today's Focus")
    st.info("**Week 1 Priority:** Cut $330/mo expenses. Launch Quick Cash services.")

def render_financial_hub():
    """Financial Hub - All money operations."""
    st.title("💰 Financial Hub")
    
    tabs = st.tabs([
        "📊 Overview",
        "🚀 Flywheel Strategy",
        "📈 10-Year Projection",
        "⚡ Quick Cash",
        "📊 Phoenix AGRO",
        "✅ Week 1 Actions"
    ])
    
    with tabs[0]:  # Overview
        st.subheader("Current Financial State")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Monthly Income", "$3,250", help="After tax")
        with col2:
            st.metric("Monthly Expenses", "$3,885")
        with col3:
            st.metric("Net Burn", "-$635/mo", delta="-$330 target")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Runway", "16 months", delta="+14mo with cuts")
        with col2:
            st.metric("Month 3 Goal", "+$3k/mo", help="Positive cash flow!")
    
    with tabs[1]:  # Flywheel
        st.subheader("🚀 Phoenix Flywheel Strategy")
        
        st.markdown("""
        ### The Compound Growth Engine
        
        **How It Works:**
        1. Trade $40k with Phoenix AGRO (3% risk, 5 positions)
        2. Generate 10-12% monthly returns
        3. Launch signal selling on Collective2/Darwinex
        4. Reinvest ALL profits + signal revenue
        5. Compound accelerates exponentially
        """)
        
        st.markdown("---")
        st.markdown("### 📅 Timeline")
        
        timeline = [
            ("**Month 1-3:** BUILD TRACK RECORD", "$40k → $45k", "Add $1k/mo from savings"),
            ("**Month 4-6:** EARLY ADOPTERS", "$45k → $58k", "First subscribers: +$1k/mo"),
            ("**Month 7-12:** SCALE UP", "$58k → $110k", "30+ subscribers: +$4.25k/mo"),
            ("**Year 1 Result:**", "$40k → $110k", "**175% growth**")
        ]
        
        for phase, result, detail in timeline:
            with st.expander(phase):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Result:** {result}")
                with col2:
                    st.markdown(f"**Detail:** {detail}")
        
        st.markdown("---")
        st.subheader("📈 10-Year Flywheel Projection")
        
        flywheel_data = [
            (2026, 40000, 40500, 110000, 14250),
            (2027, 110000, 48000, 194400, 36000),
            (2028, 194400, 60000, 305280, 36000),
            (2029, 305280, 78000, 460336, 36000),
            (2030, 460336, 96000, 667603, 36000),
            (2031, 667603, 108000, 931124, 36000),
            (2032, 931124, 45000, 1171349, 24000),
            (2033, 1171349, 57000, 1473619, 24000),
            (2034, 1473619, 69000, 1850343, 24000),
            (2035, 1850343, 69000, 2302812, 24000),
            (2036, 2302812, 69000, 2847374, 24000),
        ]
        
        for year, start, contrib, end, signals in flywheel_data:
            with st.expander(f"**{year}**"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Start", f"${start:,}")
                with col2:
                    st.metric("Contributions", f"${contrib:,}")
                with col3:
                    st.metric("End Balance", f"${end:,}")
                with col4:
                    st.metric("Signal Revenue", f"${signals:,}")
        
        st.success("**Conservative Result:** $2.97M net worth by 2036")
    
    with tabs[2]:  # 10-Year
        st.subheader("📈 10-Year Scenarios")
        
        scenario = st.radio(
            "Select Scenario:",
            ["Conservative", "Base", "Optimistic", "Optimized"]
        )
        
        scenarios = {
            "Conservative": ("$2.97M", "Phoenix steady + Quick Cash slow"),
            "Base": ("$10.1M", "Phoenix moderate + signal selling Y2"),
            "Optimistic": ("$25M", "Phoenix aggressive + exits"),
            "Optimized": ("$12.4M", "With all 20 optimizations")
        }
        
        total, desc = scenarios[scenario]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("10-Year Total", total)
        with col2:
            st.caption(desc)
    
    with tabs[3]:  # Quick Cash
        st.subheader("⚡ Quick Cash Services")
        
        services = [
            ("QR Code Generation", "$25-60", "10-15min", "$200-600/mo"),
            ("3D Model Generation", "$50-150", "30min-2hr", "$300-900/mo"),
            ("Python Automation", "$75-200", "1-3hr", "$500-1,500/mo")
        ]
        
        for name, price, time, target in services:
            with st.expander(f"✅ {name} - READY"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Price:** {price}")
                with col2:
                    st.write(f"**Time:** {time}")
                with col3:
                    st.write(f"**Target:** {target}")
        
        st.success("**Combined Target:** $1,000-3,000/mo (conservative: $300-700)")
    
    with tabs[4]:  # Phoenix AGRO
        st.subheader("📊 Phoenix AGRO MODE")
        
        phoenix_running = check_phoenix()
        status = "🟢 Active" if phoenix_running else "🔴 Offline"
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", status)
        with col2:
            st.metric("Risk Level", "3.0%")
        with col3:
            st.metric("Max Positions", "5")
        
        if phoenix_running:
            st.success("Phoenix AGRO is running. Target: $4-5k/month returns.")
        else:
            st.error("Phoenix is offline. Start it to begin generating returns.")
    
    with tabs[5]:  # Week 1
        st.subheader("✅ Week 1 Urgent Actions")
        
        st.info("**Mission:** Stop the bleeding. Launch revenue. Cut waste.")
        
        actions = [
            ("Cut $330/mo expenses", [
                "Cancel unused subscriptions (-$47/mo)",
                "Call internet provider (-$30/mo)",
                "Switch phone to prepaid (-$30/mo)",
                "Shop for insurance (-$20/mo)",
                "Start meal prep (-$150/mo)",
                "Cancel streaming service (-$13/mo)",
                "Reduce entertainment (-$50/mo)"
            ]),
            ("Launch Quick Cash (8hrs)", [
                "Set up Fiverr account (30min)",
                "Create QR Code gig (1hr)",
                "Create 3D Model gig (1hr)",
                "Create Python gig (1hr)",
                "Social media marketing (2hrs)",
                "Direct outreach (2hrs)"
            ]),
            ("S-Corp Research (3hrs)", [
                "Read IRS guide (30min)",
                "Research state requirements (30min)",
                "Find 3 attorneys (30min)",
                "Schedule consultations (30min)",
                "Make decision (1hr)"
            ])
        ]
        
        for title, items in actions:
            with st.expander(f"**{title}**"):
                for item in items:
                    checked = st.checkbox(
                        item,
                        key=f"week1_{item}",
                        value=st.session_state.week1_checklist.get(item, False)
                    )
                    st.session_state.week1_checklist[item] = checked
        
        # Progress
        total = sum(len(items) for _, items in actions)
        done = sum(1 for v in st.session_state.week1_checklist.values() if v)
        st.progress(done / total if total > 0 else 0)
        st.metric("Progress", f"{done}/{total}")

def render_operations():
    """Operations - Career + Business."""
    st.title("🏢 Operations Hub")
    
    tab1, tab2 = st.tabs(["🎯 Career", "💼 Business"])
    
    with tab1:
        st.subheader("Career Station")
        st.info("Job hunting automation - From command_center v1")
        st.markdown("[Open Full Career Station](http://localhost:8001)")
        
    with tab2:
        st.subheader("Business Operations")
        st.info("30+ services catalog - From command_center v1")
        st.markdown("[Open Full Business Station](http://localhost:8001)")

def render_engineering():
    """Engineering - CAD/3D."""
    st.title("🔧 Engineering Station")
    st.info("3D CAD generation with OpenSCAD - From command_center v1")
    st.markdown("[Open Full Engineering Station](http://localhost:8001)")

def render_ai_hub():
    """AI Hub - Assistant + Memory + Code."""
    st.title("🤖 AI Hub")
    
    tab1, tab2, tab3 = st.tabs(["💬 Assistant", "🧠 Memory", "💻 Claude Code"])
    
    with tab1:
        st.subheader("AI Assistant")
        st.info("Chat interface - From command_center v1")
        
    with tab2:
        st.subheader("Memory Search")
        st.info("Profile & preferences - From command_center v1")
        
    with tab3:
        st.subheader("Claude Code Terminal")
        st.info("Self-update capability - From command_center v1")
        
        if st.button("🚀 Launch Terminal"):
            try:
                subprocess.Popen([
                    'osascript', '-e',
                    'tell application "Terminal" to do script "claude code"'
                ])
                st.success("Terminal launched!")
            except Exception as e:
                st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════

def main():
    """Main application."""
    st.set_page_config(
        page_title="Trinity Command Center v2.1",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply Apple styling
    st.markdown(APPLE_STYLE, unsafe_allow_html=True)
    
    # Initialize
    init_session()
    
    # Sidebar
    with st.sidebar:
        # Enhanced Header
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0 0.5rem 0;">
            <h1 style="margin: 0; font-size: 1.75rem; font-weight: 700; background: linear-gradient(135deg, #0a84ff 0%, #30d158 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                🎯 TRINITY
            </h1>
            <p style="margin: 0.25rem 0 0 0; font-size: 0.7rem; color: var(--apple-text-secondary); text-transform: uppercase; letter-spacing: 2px; font-weight: 600;">
                Command Center v2.1
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # System Status Quick View
        phoenix_online = check_phoenix()
        status_emoji = "🟢" if phoenix_online else "🔴"

        st.markdown(f"""
        <div style="background: rgba(28,28,30,0.6); border-radius: 10px; padding: 0.6rem; margin-bottom: 1rem; border: 1px solid var(--apple-border);">
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem;">
                <span style="color: var(--apple-text-secondary);">Phoenix AGRO:</span>
                <span style="color: {'var(--apple-success)' if phoenix_online else 'var(--apple-danger)'}; font-weight: 600;">
                    {status_emoji} {'ACTIVE' if phoenix_online else 'OFFLINE'}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Station selector with icons
        st.markdown("**📍 NAVIGATION**")

        station_options = {
            "📊 Dashboard": "Dashboard",
            "💰 Financial Hub": "Financial Hub",
            "🏢 Operations": "Operations",
            "🔧 Engineering": "Engineering",
            "🤖 AI Hub": "AI Hub"
        }

        # Find current station display name
        current_display = [k for k, v in station_options.items() if v == st.session_state.station][0]

        station_display = st.radio(
            "Navigation:",
            list(station_options.keys()),
            index=list(station_options.keys()).index(current_display),
            label_visibility="collapsed"
        )

        station = station_options[station_display]

        if station != st.session_state.station:
            st.session_state.station = station
            st.rerun()

        # Trinity AI
        render_trinity_sidebar()

        # Enhanced Footer
        st.markdown("---")
        current_time = datetime.now().strftime('%H:%M:%S')
        st.markdown(f"""
        <div style="text-align: center; padding: 0.5rem;">
            <p style="margin: 0; font-size: 0.7rem; color: var(--apple-text-secondary);">
                ⚡ Trinity System v2.1
            </p>
            <p style="margin: 0.25rem 0 0 0; font-size: 0.65rem; color: var(--apple-text-secondary); opacity: 0.6;">
                {current_time} PST
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Render active station
    if st.session_state.station == "Dashboard":
        render_dashboard()
    elif st.session_state.station == "Financial Hub":
        render_financial_hub()
    elif st.session_state.station == "Operations":
        render_operations()
    elif st.session_state.station == "Engineering":
        render_engineering()
    elif st.session_state.station == "AI Hub":
        render_ai_hub()

if __name__ == "__main__":
    main()
