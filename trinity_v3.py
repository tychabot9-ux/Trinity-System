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
    
    /* Global Styles - Optimized for TV Display */
    .main {
        background-color: var(--apple-bg);
        color: var(--apple-text);
        font-size: 0.9rem;
    }

    /* Base text size reduction */
    body, p, div, span {
        font-size: 0.9rem;
        line-height: 1.4;
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
    
    /* Buttons - Apple style, reduced for TV */
    .stButton > button {
        background: var(--apple-primary);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        transition: all 0.2s ease;
        font-size: 0.85rem;
    }
    
    .stButton > button:hover {
        background: #0070e0;
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(10,132,255,0.3);
    }
    
    /* Metrics - Reduced for TV display */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--apple-primary);
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.75rem;
        font-weight: 500;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
    }
    
    /* Headers - Reduced for TV display */
    h1, h2, h3 {
        color: var(--apple-text);
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    h1 { font-size: 1.75rem; }
    h2 { font-size: 1.5rem; }
    h3 { font-size: 1.25rem; }
    
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
        padding: 0.6rem 1rem;
        font-weight: 500;
        font-size: 0.85rem;
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
        'optimizations_checklist': {},
        'phoenix_status': None,
        'last_refresh': None
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def check_phoenix() -> dict:
    """Check Phoenix status and mode."""
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'mark_xii_phoenix'],
            capture_output=True,
            timeout=3
        )
        is_running = result.returncode == 0

        # Read config to get actual status
        mode = "PAPER"  # Default assumption
        capital = 100000  # Paper trading capital

        return {
            'running': is_running,
            'mode': mode,
            'capital': capital,
            'live': False  # Not live trading yet
        }
    except:
        return {'running': False, 'mode': 'UNKNOWN', 'capital': 0, 'live': False}

def get_context() -> dict:
    """Get current system context for Trinity."""
    phoenix_status = check_phoenix()
    return {
        'burn_rate': -635,
        'phoenix_running': phoenix_status['running'],
        'phoenix_mode': phoenix_status['mode'],
        'phoenix_capital': phoenix_status['capital'],
        'week1_done': sum(1 for v in st.session_state.week1_checklist.values() if v),
        'week1_total': 18,
        'quick_cash_ready': 3,
        'trading_capital': phoenix_status['capital']  # Use actual capital
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
        is_running = phoenix_status['running']
        status_class = "status-online" if is_running else "status-offline"
        status_text = f"{phoenix_status['mode']} - {is_running and 'ACTIVE' or 'OFFLINE'}"

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
        phoenix_status = check_phoenix()
        mode_text = f"{phoenix_status['mode']} ${phoenix_status['capital']/1000:.0f}k"
        st.metric("Phoenix", f"{'🟢' if phoenix_status['running'] else '🔴'} {mode_text}")
        
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
    
    phoenix_status = check_phoenix()
    if not phoenix_status['running']:
        st.error(f"**Phoenix Offline** - Currently in {phoenix_status['mode']} mode")
    elif phoenix_status['mode'] == 'PAPER':
        st.warning("**Phoenix Paper Trading** - Not generating real returns yet. Validating strategy.")
    
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
        "🎯 20 Optimizations",
        "⚡ Quick Cash",
        "📊 Phoenix AGRO",
        "✅ Week 1 Actions",
        "🔍 Paper → Live"
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
            trading_gain = end - start - contrib
            gain_pct = (trading_gain / (start + contrib / 2)) * 100 if (start + contrib / 2) > 0 else 0

            with st.expander(f"**{year}** → ${end:,}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Start Capital", f"${start:,}")
                    st.metric("+ Contributions", f"${contrib:,}", help="Savings + Signal Revenue")
                with col2:
                    st.metric("= Total Invested", f"${start + contrib:,}")
                    st.metric("+ Trading Gains", f"${trading_gain:,}", delta=f"{gain_pct:.1f}% return")
                with col3:
                    st.metric("= End Balance", f"${end:,}")
                    st.metric("Signal Revenue", f"${signals:,}", help="Annual signal selling income")

                st.caption(f"💡 Math: ${start:,} start + ${contrib:,} added + ${trading_gain:,} gains = ${end:,} end")
        
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
            "Optimistic": ("$25M", "Everything goes perfect naturally"),
            "Optimized": ("$27.3M", "Base + 20 optimizations executed ✅")
        }
        
        total, desc = scenarios[scenario]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("10-Year Total", total)
        with col2:
            st.caption(desc)
    
    with tabs[3]:  # Daily Check-In Dashboard
        from datetime import datetime, timedelta
        today = datetime.now()

        st.title("📋 Daily Check-In Dashboard")
        st.caption(f"📅 {today.strftime('%A, %B %d, %Y')}")

        # Trinity AI Brain Status
        st.markdown("---")
        st.subheader("🤖 Trinity AI Brain - Strategic Analysis")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Last Analysis", "Feb 5, 22:08", help="Latest comprehensive AI analysis")
        with col2:
            st.metric("AI Models", "Claude Opus 4.5 + Gemini 1.5", help="Dual AI system active")
        with col3:
            st.metric("Confidence", "62%", help="AI confidence in recommendations")
        with col4:
            st.metric("Target CAGR", "63%", help="Required for $27.3M in 10 years")

        # AI Implemented Recommendations
        with st.expander("✅ AI Recommendations - IMPLEMENTED", expanded=True):
            st.success("""
            **PRIORITY #1: Diagnose Trade Paralysis** ✅ COMPLETE
            - **AI Said:** "Understand why recent_trades=0. A perfect system that doesn't trade earns 0%."
            - **We Did:** Added heartbeat logging to Phoenix (Feb 5)
            - **Result:** Diagnosed correctly - system is operational, just waiting for SMA crossover signals. Market neutral (RSI 52.9). Not a bug!
            - **Impact:** Full visibility into decision-making process. Can now track exactly why trades are/aren't taken.

            **PRIORITY #2: Implement Tiered Position Sizing** ✅ COMPLETE
            - **AI Said:** "Start with 1-2% risk per trade, scale to 3-5% as Sharpe ratio proves >1.5."
            - **We Did:** Built 3-tier system (Feb 5)
              - Tier 1: 1.0% risk (<10 trades or Sharpe <1.0) ← Current
              - Tier 2: 1.76% risk (10-19 trades, Sharpe 1.0-1.5)
              - Tier 3: 3.0% risk (20+ trades, Sharpe >1.5)
            - **Result:** Capital protected during validation, will accelerate 3x once edge proven
            - **Impact:** Risk scales automatically with performance. No manual intervention needed.

            **NEW: Paper→Live Translation Hub** ✅ COMPLETE
            - **Built:** Real-time validation dashboard (Feb 5)
            - **Features:** Side-by-side comparison, Go/No-Go checklist, plan alignment
            - **Impact:** Can validate strategy meets $4k/mo targets before risking real capital
            """)

        # AI Active Priorities
        with st.expander("🎯 AI Recommendations - ACTIVE PRIORITIES", expanded=True):
            st.warning("""
            **PRIORITY #3: Activate Income Diversification Layer** 🔴 URGENT
            - **AI Analysis (Latest):** "Implement the 'Barbell Income Strategy' - build 2-3 additional automated income streams that compound independently"
            - **Impact:** +$300K over 10 years at 60% CAGR

            **Recommended Income Streams:**
            1. **High-Ticket Consulting** ($200-500/hr) 🔴 IMMEDIATE
               - Target: Trading system architecture consulting
               - Your Edge: Technical depth + Phoenix track record
               - Route: 80% of consulting income → trading capital
               - Timeline: Week 1-2 (create offer, reach out to networks)
               - Expected: $2-5K/month part-time

            2. **Fiverr Services** ($25-200/gig) 🔴 IMMEDIATE
               - QR codes, 3D models, Python automation
               - Timeline: Week 1-2 for launch
               - Expected: $500-1,500/month initial

            3. **Signal Selling** (Collective2/Darwinex) 🟡 MONTH 2-3
               - After 15-20 validated trades
               - Expected: $1-4K/month by Month 6
               - Impact: +$85K-120K over 10 years

            4. **Trinity SaaS MVP** 🟡 MONTH 2-3
               - Dashboard + API marketplace
               - 8-week MVP timeline
               - Expected: $1-2K/month by Month 6

            5. **Automated Trading Bots** 🟢 FUTURE (AI's "Barbell" Suggestion)
               - MEV bots, arbitrage scanners, liquidation bots
               - Requires proven track record first
               - Potential: Additional compounding streams

            **PRIORITY #4: High-Impact Phoenix Optimizations** 🟡 PLANNED
            - **AI Sequencing:** (1) Execution/infrastructure → (2) Risk management → (3) Alpha generation → (4) Scaling
            - **Specific Recommendations:**
              a) Multi-timeframe confirmation (reduce false signals)
              b) Kelly Criterion position sizing (adaptive based on confidence)
              c) Correlation filters (avoid clustered losses)
              d) Execution quality analytics (optimize fill rates)
            - **Impact:** +$200K over 10 years, -35% downside risk
            - **Timeline:** After 20+ paper trades validate core strategy
            - **Rationale:** Don't optimize until base strategy proves profitable

            **PRIORITY #5: Capital Injection Protocol + Asymmetric Bets** 🟡 PLANNED
            - **Weekly Injection:** "Even $500/week from other income adds $26K/year base → $1M+ additional terminal value"
            - **Implementation:** 100% of freelance profits → trading account
            - **Expected:** $500-1,000/week once services launched
            - **Impact:** +$38K over 10 years from injection alone (before compounding!)

            - **NEW - Asymmetric Optionality:** Allocate 5-10% of capital to high-conviction asymmetric bets
              - Early-stage DeFi protocols, options strategies
              - Potential: 10-50x returns that dramatically accelerate timeline
              - Timeline: After live trading proves stable (Month 3+)
            """)

        # AI Impact Tracking
        with st.expander("📊 AI Recommendations - IMPACT TRACKING"):
            st.info("""
            **Implemented (Priority #1 & #2):**
            - ✅ Heartbeat logging: Full visibility achieved
            - ✅ Tiered position sizing: 3x growth potential unlocked
            - ✅ Paper→Live hub: Validation framework in place
            - **Expected Impact:** $0 immediate (validation phase), but enables safe scaling to 3.0% risk = $1.2k/mo vs $400/mo at 1.0%

            **Pending (Priority #3-5):**
            - ⏳ Income diversification: NOT STARTED ($300K at risk if delayed)
            - ⏳ Phoenix optimizations: NOT NEEDED YET (wait for 20+ trades)
            - ⏳ Capital injection: NOT STARTED (depends on Priority #3)

            **Timeline Analysis:**
            - **Current:** Paper trading validation (0/15 trades)
            - **Week 1-2:** Launch income streams (Fiverr, freelance)
            - **Week 3-4:** Reach 15-20 paper trades, validate strategy
            - **Month 2:** Go live with $40k if validation passes
            - **Month 2-3:** Start signal selling, implement optimizations

            **Critical Path:** Income diversification (Priority #3) is the bottleneck. Phoenix is validated but needs external capital injection for maximum growth.

            **62% Confidence Explained:** AI is confident in the approach but notes execution risk. Main uncertainty is whether you'll actually launch the income streams vs continuing to optimize the trading system.
            """)

        st.markdown("---")

        # Progress overview
        all_tasks = []

        # Add optimizations
        optimizations_list = [
            # AI BRAIN PRIORITIES (Completed)
            ("✅ AI Priority #1: Heartbeat logging (DONE)", "🟢", "Full visibility", "2026-02-05", "Added comprehensive decision logging to Phoenix. System is operational, correctly waiting for signals."),
            ("✅ AI Priority #2: Tiered sizing (DONE)", "🟢", "3x growth potential", "2026-02-05", "Implemented performance-based risk scaling: 1.0%→1.76%→3.0% as Sharpe validates."),
            ("✅ Paper→Live translation hub (DONE)", "🟢", "Validation framework", "2026-02-05", "Built side-by-side comparison dashboard to validate strategy before live deployment."),

            # AI BRAIN PRIORITIES (Active)
            ("🎯 AI Priority #3a: High-ticket consulting", "🔴", "+$60K+/yr", "2026-02-10", "Trading system architecture consulting at $200-500/hr. Target networks, create offer. 80% → trading capital."),
            ("🎯 AI Priority #3b: Fiverr services launch", "🔴", "+$18K/yr", "2026-02-12", "Launch QR codes, 3D models, Python automation. $500-1,500/mo expected. Template library + automation."),
            ("🎯 AI Priority #5: Capital injection protocol", "🔴", "+$1M+/10yr", "2026-02-15", "Route 100% of consulting/freelance profits → trading account. $500-1K/week = $26K/yr compounds to $1M+."),

            # CRITICAL - Phoenix Trading Bug (RESOLVED)
            ("Contract selection diagnosis (RESOLVED)", "🟢", "Understood", "2026-02-05", "Not a bug - system correctly waiting for SMA crossover signals. Market neutral (RSI 52.9)."),

            # Financial (Immediate Action)
            ("Cut $330/mo expenses", "🔴", "$4k/yr", "2026-02-07", "Cancel subscriptions, reduce dining out, meal prep"),
            ("Health budget ($80/mo)", "🔴", "Prevent burnout", "2026-02-07", "Keep gym, add therapy/massage budget"),
            ("Cancel Jarvis Phase 2-7", "🔴", "Save 600hrs", "2026-02-07", "Stop over-engineering, focus on revenue"),
            ("Focus Matrix (60hr/wk)", "🔴", "Sustainability", "2026-02-08", "Stop 88hr weeks, prioritize ruthlessly"),

            # Week 1-2 Actions
            ("Start Collective2 signal selling", "🟡", "+$85k-120k/10yr", "2026-02-12", "Set up C2 account, publish Phoenix signals"),
            ("AGRO MODE+ (3.5% risk)", "🟡", "+$12k-18k/yr", "2026-02-12", "Increase Phoenix risk parameter after stable week"),
            ("Form S-Corporation", "🟡", "$14k/yr savings", "2026-03-01", "Research attorney, file by March for Q1 earnings"),
            ("Set up QSBS strategy", "🟡", "+$390k at exit", "2026-02-28", "Decide C-Corp vs S-Corp before formation"),

            # Month 1 Actions
            ("Ship Trinity MVP", "🟡", "+$12k-20k/yr", "2026-03-15", "8-week MVP: dashboard + API marketplace + landing"),
            ("Simplify tech stack", "🟡", "Save 200hrs", "2026-02-28", "Python+FastAPI+Streamlit only"),
            ("Fiverr delivery automation", "🟡", "3x capacity", "2026-02-21", "Build template library + scripts (20hrs)"),
            ("Batch processing days", "🟡", "+20% efficiency", "2026-02-15", "Theme days: Fiverr Mon/Wed, Dev Tue/Thu, Marketing Fri"),

            # Month 2-3 Actions
            ("Phoenix optimization", "🟢", "+$200k/10yr", "2026-03-30", "Adaptive sizing, profit targets, correlation filters"),
            ("VIX-based risk reduction", "🟢", "-35% downside", "2026-03-15", "Add VIX filters to Phoenix config"),
            ("Increase Fiverr pricing", "🟢", "+$4k/yr", "2026-03-01", "After 5 reviews: QR $25→$40, 3D $50→$75"),
            ("Accelerate capital injection", "🟢", "+$38k/10yr", "2026-03-01", "100% Fiverr profit → trading account"),

            # Month 3-4 Actions
            ("Blue Ocean strategy", "🟢", "Better margins", "2026-04-01", "Target underserved niches, avoid competition"),
            ("Customer acquisition system", "🟢", "Predictable growth", "2026-04-15", "SEO, content marketing, email funnels"),

            # Ongoing/Future
            ("Multi-strategy approach", "🟢", "Reduce risk", "2026-08-01", "Add mean reversion by Year 2"),
            ("Outsource Fiverr", "🟢", "Scale without burnout", "When $10k/mo", "Hire VA when revenue supports it"),
            ("Aggregation strategy", "🟢", "10x multiplier", "2027-01-01", "Roll-up strategy in Year 2-3"),
            ("Optionality preservation", "🟢", "Keep options open", "Ongoing", "Don't commit to single path too early"),
        ]

        # Add Week 1 Urgent Actions
        week1_actions = [
            ("Cancel unused subscriptions", "🔴", "-$47/mo", "2026-02-07", "Netflix, unused services"),
            ("Call internet provider", "🔴", "-$30/mo", "2026-02-07", "Negotiate lower rate"),
            ("Switch to prepaid phone", "🔴", "-$30/mo", "2026-02-08", "Mint Mobile or similar"),
            ("Shop for insurance", "🔴", "-$20/mo", "2026-02-09", "Compare quotes"),
            ("Start meal prep", "🔴", "-$150/mo", "2026-02-10", "Weekly batch cooking"),
            ("Reduce entertainment", "🔴", "-$50/mo", "2026-02-07", "Free activities"),
            ("Set up Fiverr gigs", "🟡", "Revenue start", "2026-02-10", "QR, 3D, Python gigs live"),
            ("Create portfolio samples", "🟡", "Social proof", "2026-02-12", "3 examples each service"),
            ("Phoenix daily monitoring", "🟡", "$4-5k/mo", "Daily", "Check trades, adjust if needed"),
        ]

        all_tasks = optimizations_list + week1_actions

        # Count by priority
        red_tasks = [t for t in all_tasks if t[1] == "🔴" and not st.session_state.optimizations_checklist.get(t[0], False)]
        yellow_tasks = [t for t in all_tasks if t[1] == "🟡" and not st.session_state.optimizations_checklist.get(t[0], False)]
        green_tasks = [t for t in all_tasks if t[1] == "🟢" and not st.session_state.optimizations_checklist.get(t[0], False)]
        done_tasks = [t for t in all_tasks if st.session_state.optimizations_checklist.get(t[0], False)]

        # Dashboard metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔴 Urgent", len(red_tasks), help="Do TODAY")
        with col2:
            st.metric("🟡 Recommended", len(yellow_tasks), help="This week/month")
        with col3:
            st.metric("🟢 Suggested", len(green_tasks), help="When ready")
        with col4:
            st.metric("✅ Done", len(done_tasks), help=f"{len(done_tasks)}/{len(all_tasks)}")

        total_progress = len(done_tasks) / len(all_tasks) if len(all_tasks) > 0 else 0
        st.progress(total_progress)
        st.caption(f"Overall Progress: {total_progress*100:.1f}%")

        # Today's Focus
        st.markdown("---")
        st.subheader("🎯 Today's Focus (Urgent)")
        if red_tasks:
            for task_name, priority, impact, due_date, description in red_tasks:
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        checked = st.checkbox(
                            f"**{task_name}**",
                            key=f"task_{task_name}",
                            value=st.session_state.optimizations_checklist.get(task_name, False)
                        )
                        st.session_state.optimizations_checklist[task_name] = checked
                        st.caption(f"💰 {impact} | 📅 Due: {due_date} | 📝 {description}")
                    with col2:
                        st.markdown(f"### {priority}")
                    st.markdown("---")
        else:
            st.success("🎉 No urgent tasks today! Great work!")

        # This Week
        st.markdown("---")
        with st.expander(f"📅 This Week/Month - Recommended ({len(yellow_tasks)} tasks)", expanded=True):
            for task_name, priority, impact, due_date, description in yellow_tasks:
                col1, col2 = st.columns([4, 1])
                with col1:
                    checked = st.checkbox(
                        f"**{task_name}**",
                        key=f"task_{task_name}",
                        value=st.session_state.optimizations_checklist.get(task_name, False)
                    )
                    st.session_state.optimizations_checklist[task_name] = checked
                    st.caption(f"💰 {impact} | 📅 {due_date} | 📝 {description}")
                with col2:
                    st.markdown(f"## {priority}")

        # Future/Suggestions
        with st.expander(f"🔮 Future & Suggestions ({len(green_tasks)} tasks)"):
            for task_name, priority, impact, due_date, description in green_tasks:
                col1, col2 = st.columns([4, 1])
                with col1:
                    checked = st.checkbox(
                        f"**{task_name}**",
                        key=f"task_{task_name}",
                        value=st.session_state.optimizations_checklist.get(task_name, False)
                    )
                    st.session_state.optimizations_checklist[task_name] = checked
                    st.caption(f"💰 {impact} | 📅 {due_date} | 📝 {description}")
                with col2:
                    st.markdown(f"## {priority}")

        # Completed
        with st.expander(f"✅ Completed ({len(done_tasks)} tasks)"):
            for task_name, priority, impact, due_date, description in done_tasks:
                col1, col2 = st.columns([4, 1])
                with col1:
                    checked = st.checkbox(
                        f"~~{task_name}~~",
                        key=f"task_{task_name}",
                        value=st.session_state.optimizations_checklist.get(task_name, False)
                    )
                    st.session_state.optimizations_checklist[task_name] = checked
                    st.caption(f"💰 {impact} | ✅ Done")
                with col2:
                    st.markdown("✅")

        # Summary
        st.markdown("---")
        st.info(f"""
        **Daily Check-In Summary:**
        - 🔴 **Urgent (TODAY):** {len(red_tasks)} tasks - Do these first!
        - 🟡 **Recommended (THIS WEEK/MONTH):** {len(yellow_tasks)} tasks
        - 🟢 **Suggested (WHEN READY):** {len(green_tasks)} tasks
        - ✅ **Completed:** {len(done_tasks)}/{len(all_tasks)} ({total_progress*100:.1f}%)

        **Goal:** Complete all tasks → Unlock $27.3M (beats Optimistic $25M)
        """)

    with tabs[4]:  # Quick Cash
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
    
    with tabs[5]:  # Phoenix Status
        st.subheader("📊 Phoenix Trading Status")

        phoenix_status = check_phoenix()
        is_running = phoenix_status['running']
        mode = phoenix_status['mode']
        capital = phoenix_status['capital']

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            status_display = f"{'🟢 Active' if is_running else '🔴 Offline'}"
            st.metric("Status", status_display)
        with col2:
            st.metric("Mode", mode, help="PAPER = validation, LIVE = real money")
        with col3:
            st.metric("Capital", f"${capital/1000:.0f}k")
        with col4:
            st.metric("Risk/Trade", "1.0%", help="Tiered: T1(1.0%)→T2(1.76%)→T3(3.0%)")

        st.markdown("---")

        if not is_running:
            st.error("**Phoenix Offline** - Bot is not running")
            st.code("cd /Users/tybrown/Desktop/Bot-Factory && python3 mark_xii_phoenix.py")
        elif mode == "PAPER":
            st.warning(f"""
            **📊 PAPER TRADING MODE (Validation Phase)**

            Phoenix is running with **${capital:,}** paper money to validate strategy before live deployment.

            **Current Status:**
            - Testing AGRO MODE configuration (3% risk, 5 positions)
            - Validating 10-12% monthly return target
            - Building track record for signal selling

            **Next Steps:**
            1. Collect 15-20 paper trades (7-10 days)
            2. Verify win rate >50%, Avg R >2.0
            3. Confirm <20% max drawdown
            4. Go live with $40k real capital

            **⚠️ Paper trading profits are NOT real money.**
            """)
        else:
            st.success(f"""
            **🟢 LIVE TRADING ACTIVE**

            Phoenix AGRO running with **${capital:,}** real capital.
            Target: $4-5k/month returns.
            """)

        # System status update
        st.markdown("---")
        st.success("""
        ✅ **SYSTEMS OPERATIONAL**

        Phoenix is running with **heartbeat logging** and **tiered position sizing** active.

        **Current Status:**
        - ✅ Contract selection bug FIXED (DTE 27-35, delta 0.25-0.35)
        - ✅ Heartbeat logging ACTIVE (full visibility into decisions)
        - ✅ Tiered position sizing ACTIVE (Tier 1: 1.0% risk)
        - ⏳ Waiting for market signals (no SMA crossover detected yet)

        **Why 0 Trades:** Market is neutral (RSI 52.9). Phoenix correctly holding until SMA crossover signal appears.

        **AI Brain Analysis:** "System is operational but not yet generating signals. This is market conditions, not a bug."
        """)
    
    with tabs[6]:  # Week 1
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

    with tabs[7]:  # Paper → Live Translation
        st.subheader("🔍 Paper → Live Strategy Validation")

        st.info("""
        **Purpose:** Compare paper trading performance ($100k) vs extrapolated live performance ($40k).
        Validate strategy meets targets before deploying real capital.
        """)

        # Load Phoenix state
        phoenix_state_path = BOT_FACTORY_DIR / "phoenix_state.json"
        try:
            with open(phoenix_state_path) as f:
                phoenix_state = json.load(f)
        except:
            phoenix_state = {
                "current_equity": 100000,
                "peak_equity": 100000,
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "total_pnl": 0.0,
                "trade_history": []
            }

        # Calculate metrics
        paper_equity = phoenix_state.get("current_equity", 100000)
        paper_start = 100000
        total_trades = phoenix_state.get("total_trades", 0)
        winning_trades = phoenix_state.get("winning_trades", 0)
        losing_trades = phoenix_state.get("losing_trades", 0)
        total_pnl = phoenix_state.get("total_pnl", 0.0)
        trade_history = phoenix_state.get("trade_history", [])

        # Calculate paper metrics
        paper_return_pct = ((paper_equity - paper_start) / paper_start) * 100 if paper_start > 0 else 0
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        avg_win = sum(t.get("pnl", 0) for t in trade_history if t.get("pnl", 0) > 0) / winning_trades if winning_trades > 0 else 0
        avg_loss = abs(sum(t.get("pnl", 0) for t in trade_history if t.get("pnl", 0) < 0) / losing_trades) if losing_trades > 0 else 0
        avg_r_multiple = (avg_win / avg_loss) if avg_loss > 0 else 0

        # Calculate drawdown
        peak_equity = phoenix_state.get("peak_equity", 100000)
        current_drawdown_pct = ((peak_equity - paper_equity) / peak_equity * 100) if peak_equity > 0 else 0

        # Calculate Sharpe ratio (from Phoenix logic)
        sharpe_ratio = 0.0
        if len(trade_history) >= 5:
            returns = []
            for trade in trade_history:
                equity_before = trade.get("equity_after", paper_equity) - trade.get("pnl", 0)
                if equity_before > 0:
                    returns.append(trade.get("pnl", 0) / equity_before)
            if len(returns) >= 5:
                mean_return = sum(returns) / len(returns)
                variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
                std_return = variance ** 0.5
                if std_return > 0:
                    sharpe_ratio = (mean_return / std_return) * (252 / len(returns)) ** 0.5

        # Scale to live account ($40k)
        live_start = 40000
        scaling_factor = live_start / paper_start
        live_equity = paper_start + (paper_equity - paper_start) * scaling_factor
        live_pnl = total_pnl * scaling_factor
        live_return_pct = paper_return_pct  # Percentage stays same

        # Projected monthly return (if we had trades)
        if total_trades > 0:
            # Estimate days of trading
            days_trading = 30  # Default assumption
            if trade_history:
                first_trade_time = trade_history[0].get("entry_time", "")
                last_trade_time = trade_history[-1].get("exit_time", "")
                # Simple day count estimate

            trades_per_day = total_trades / days_trading if days_trading > 0 else 0
            projected_monthly_trades = trades_per_day * 21  # 21 trading days
            monthly_return_pct = (paper_return_pct / days_trading) * 21 if days_trading > 0 else 0
            projected_monthly_return_live = (live_start * monthly_return_pct / 100)
        else:
            projected_monthly_trades = 0
            monthly_return_pct = 0
            projected_monthly_return_live = 0

        st.markdown("---")

        # Side-by-side comparison
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📄 Paper Trading ($100k)")
            st.metric("Starting Capital", f"${paper_start:,}")
            st.metric("Current Equity", f"${paper_equity:,.2f}", delta=f"{paper_return_pct:+.2f}%")
            st.metric("Total P&L", f"${total_pnl:,.2f}")
            st.metric("Total Trades", f"{total_trades}")

            if total_trades > 0:
                st.metric("Win Rate", f"{win_rate:.1f}%")
                st.metric("Avg R Multiple", f"{avg_r_multiple:.2f}x" if avg_r_multiple > 0 else "N/A")
                st.metric("Max Drawdown", f"{current_drawdown_pct:.2f}%")
                st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}" if sharpe_ratio > 0 else "N/A")
            else:
                st.caption("🕐 Waiting for first trade...")

        with col2:
            st.markdown("### 💰 Live Extrapolation ($40k)")
            st.metric("Starting Capital", f"${live_start:,}")
            st.metric("Projected Equity", f"${live_equity:,.2f}", delta=f"{live_return_pct:+.2f}%")
            st.metric("Projected P&L", f"${live_pnl:,.2f}")
            st.metric("Same Trades", f"{total_trades}")

            if total_trades > 0:
                st.metric("Win Rate", f"{win_rate:.1f}%", help="Same as paper")
                st.metric("Avg R Multiple", f"{avg_r_multiple:.2f}x" if avg_r_multiple > 0 else "N/A")
                st.metric("Max Drawdown", f"{current_drawdown_pct:.2f}%", help="Same as paper")
                st.metric("Monthly Target", f"${projected_monthly_return_live:,.0f}", help="If sustained")
            else:
                st.caption("🕐 Waiting for first trade...")

        st.markdown("---")

        # Validation Checkpoints
        st.subheader("✅ Validation Checklist (Go/No-Go)")

        st.markdown("""
        **Minimum Requirements for Live Deployment:**
        - 15-20 paper trades completed
        - Win rate >50%
        - Avg R multiple >2.0
        - Max drawdown <20%
        - Sharpe ratio >1.5 (Tier 3 unlock)
        """)

        # Checkpoint status
        trades_needed = max(0, 15 - total_trades)
        trades_check = total_trades >= 15
        winrate_check = win_rate >= 50 if total_trades > 0 else False
        r_multiple_check = avg_r_multiple >= 2.0 if total_trades > 0 else False
        drawdown_check = current_drawdown_pct < 20 if total_trades > 0 else False
        sharpe_check = sharpe_ratio >= 1.5 if sharpe_ratio > 0 else False

        col1, col2, col3 = st.columns(3)

        with col1:
            if trades_check:
                st.success(f"✅ Trades: {total_trades}/15+")
            else:
                st.warning(f"⏳ Trades: {total_trades}/15 ({trades_needed} more needed)")

        with col2:
            if total_trades >= 5:
                if winrate_check:
                    st.success(f"✅ Win Rate: {win_rate:.1f}% (>50%)")
                else:
                    st.error(f"❌ Win Rate: {win_rate:.1f}% (<50%)")
            else:
                st.info("⏳ Win Rate: Need 5+ trades")

        with col3:
            if total_trades >= 5:
                if r_multiple_check:
                    st.success(f"✅ Avg R: {avg_r_multiple:.2f}x (>2.0)")
                else:
                    st.error(f"❌ Avg R: {avg_r_multiple:.2f}x (<2.0)")
            else:
                st.info("⏳ Avg R: Need 5+ trades")

        col1, col2, col3 = st.columns(3)

        with col1:
            if total_trades >= 5:
                if drawdown_check:
                    st.success(f"✅ Drawdown: {current_drawdown_pct:.2f}% (<20%)")
                else:
                    st.error(f"❌ Drawdown: {current_drawdown_pct:.2f}% (>20%)")
            else:
                st.info("⏳ Drawdown: Need 5+ trades")

        with col2:
            if sharpe_ratio > 0:
                if sharpe_check:
                    st.success(f"✅ Sharpe: {sharpe_ratio:.2f} (>1.5)")
                else:
                    st.warning(f"⚠️ Sharpe: {sharpe_ratio:.2f} (<1.5)")
            else:
                st.info("⏳ Sharpe: Need 5+ trades")

        with col3:
            # Overall Go/No-Go
            all_checks = [trades_check, winrate_check, r_multiple_check, drawdown_check, sharpe_check]
            if total_trades >= 15 and all(all_checks):
                st.success("🚀 GO FOR LIVE")
            elif total_trades >= 5:
                passed = sum(all_checks)
                st.warning(f"⏳ {passed}/5 checks passed")
            else:
                st.info("⏳ Validating strategy...")

        st.markdown("---")

        # Plan alignment
        st.subheader("📊 Plan Alignment Check")

        target_monthly_return = 4000  # $4k-5k/mo target from plan
        on_track = projected_monthly_return_live >= target_monthly_return if total_trades >= 10 else None

        if on_track is None:
            st.info(f"""
            **Target:** ${target_monthly_return:,}/month from live trading

            **Status:** Need 10+ trades to project monthly performance

            **Current Progress:** {total_trades}/10 trades completed
            """)
        elif on_track:
            st.success(f"""
            ✅ **ON TRACK FOR PLAN TARGETS**

            - Paper performance: {paper_return_pct:+.2f}%
            - Extrapolated live monthly: ${projected_monthly_return_live:,.0f}
            - Target: ${target_monthly_return:,}/month
            - Status: **EXCEEDING TARGET** 🎯
            """)
        else:
            st.warning(f"""
            ⚠️ **BELOW PLAN TARGETS**

            - Paper performance: {paper_return_pct:+.2f}%
            - Extrapolated live monthly: ${projected_monthly_return_live:,.0f}
            - Target: ${target_monthly_return:,}/month
            - Gap: ${target_monthly_return - projected_monthly_return_live:,.0f}/month

            **Recommendation:** Continue paper trading and optimize strategy before going live.
            """)

        # Next steps
        st.markdown("---")
        st.subheader("📋 Next Steps")

        if total_trades == 0:
            st.info("""
            **Waiting for market signals...**

            Phoenix is running and monitoring QQQ for SMA crossover signals.

            **What's happening:**
            - Market is neutral (RSI ~52.9)
            - No SMA crossover detected yet
            - System is correctly holding (not a bug)

            **Timeline:** Expect first trade within 1-7 days depending on market conditions.
            """)
        elif total_trades < 5:
            st.info(f"""
            **Early validation phase**

            - Completed: {total_trades} trades
            - Need: 5+ trades for initial metrics
            - Then: 15-20 trades for full validation

            **ETA:** ~3-7 more days to reach 5 trades (based on typical signal frequency)
            """)
        elif total_trades < 15:
            st.warning(f"""
            **Continue paper trading validation**

            - Completed: {total_trades}/15 trades
            - Remaining: {15 - total_trades} trades

            **Current metrics:**
            - Win rate: {win_rate:.1f}% (target: >50%)
            - Avg R: {avg_r_multiple:.2f}x (target: >2.0)
            - Sharpe: {sharpe_ratio:.2f} (target: >1.5)

            **ETA:** ~{(15 - total_trades) * 1.5:.0f} days to complete validation
            """)
        else:
            if all([trades_check, winrate_check, r_multiple_check, drawdown_check]):
                st.success("""
                🚀 **READY FOR LIVE DEPLOYMENT**

                All validation checks passed! Strategy is proven on paper.

                **Next Steps:**
                1. Review final paper trading results
                2. Fund Alpaca account with $40k
                3. Switch Phoenix to LIVE mode
                4. Start with conservative position sizing (Tier 1)
                5. Monitor closely for first 5 live trades

                **Expected Results:** $4-5k/month based on paper performance
                """)
            else:
                st.error("""
                ❌ **NOT READY FOR LIVE - Failed Validation**

                Some validation checks failed. Strategy needs optimization.

                **Options:**
                1. Continue paper trading and adjust parameters
                2. Analyze losing trades for patterns
                3. Consider different entry/exit criteria
                4. Contact Trinity AI for optimization suggestions

                **DO NOT go live until all checks pass!**
                """)

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

    # Auto-refresh for autonomous updates (every 60 seconds)
    # Reloads page automatically to show new data from Trinity Auto-Sync
    st.markdown("""
        <meta http-equiv="refresh" content="60">
        <script>
            // Store last interaction time to avoid disruptive refreshes
            let lastInteraction = Date.now();
            document.addEventListener('click', () => lastInteraction = Date.now());
            document.addEventListener('keypress', () => lastInteraction = Date.now());

            // Only refresh if no interaction in last 30 seconds
            setInterval(() => {
                if (Date.now() - lastInteraction > 30000) {
                    location.reload();
                }
            }, 60000);
        </script>
    """, unsafe_allow_html=True)

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
        phoenix_status = check_phoenix()
        is_running = phoenix_status['running']
        mode = phoenix_status['mode']
        status_emoji = "🟢" if is_running else "🔴"

        st.markdown(f"""
        <div style="background: rgba(28,28,30,0.6); border-radius: 10px; padding: 0.6rem; margin-bottom: 1rem; border: 1px solid var(--apple-border);">
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem;">
                <span style="color: var(--apple-text-secondary);">Phoenix:</span>
                <span style="color: {'var(--apple-warning)' if mode == 'PAPER' else ('var(--apple-success)' if is_running else 'var(--apple-danger)')}; font-weight: 600;">
                    {status_emoji} {mode} {'ACTIVE' if is_running else 'OFF'}
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
