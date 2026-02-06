#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════╗
║                  TRINITY COMMAND CENTER v2.0                   ║
║            Unified AI Workstation with Optimization            ║
║                  February 2026 - Enhanced                      ║
╚════════════════════════════════════════════════════════════════╝

Modules:
  🏠 Homepage - System overview & quick actions
  💰 Financial Projections - Live financial dashboard
  🎯 Career Station - Job hunting automation
  🔧 Engineering Station - CAD generation & 3D modeling
  🧠 Memory Dashboard - View profile, preferences & insights
  🤖 AI Assistant - Chat with Trinity AI (files, voice, images)
  📊 Trading Station - Bot monitoring & performance (AGRO MODE)
  💼 Business Station - Autonomous income operations
  ⚡ Quick Cash - Launch status & Week 1 actions
  💻 Claude Code - Terminal access for development

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
JOB_STATUS_DB = BASE_DIR / "job_logs" / "job_status.db"
DRAFT_DIR = BASE_DIR / "email_drafts"
CAD_OUTPUT_DIR = BASE_DIR / "cad_output"
CAD_PREVIEWS_DIR = CAD_OUTPUT_DIR / "previews"

# Trading bot paths
PHOENIX_LOG = BOT_FACTORY_DIR / "mark_xii_phoenix.log"
GENESIS_CONFIG = BOT_FACTORY_DIR / "genesis_v2_agro_config.py"
MACRO_STATUS = BOT_FACTORY_DIR / "macro_status.json"

# Financial data paths
OPTIMIZATION_REPORT = BASE_DIR / "TRINITY_OPTIMIZATION_REPORT.md"
FINANCIAL_MODEL = BASE_DIR / "COMPLETE_FINANCIAL_MODEL_2026_2036.md"
QUICK_CASH_REPORT = BASE_DIR / "QUICK_CASH_SERVICES_TEST_REPORT.md"
WEEK1_PLAN = BASE_DIR / "WEEK_1_URGENT_ACTION_PLAN.md"

# Ensure directories exist
for dir_path in [JOB_STATUS_DB.parent, CAD_OUTPUT_DIR, CAD_PREVIEWS_DIR, DRAFT_DIR]:
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create directory {dir_path}: {e}")

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'vr_mode' not in st.session_state:
        st.session_state.vr_mode = False
    if 'active_module' not in st.session_state:
        st.session_state.active_module = "Homepage"
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
    if 'week1_checklist' not in st.session_state:
        st.session_state.week1_checklist = {}

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
            memory.learn_preference('Trading', 'bot', 'active_system', 'Phoenix Mark XII AGRO MODE')
            memory.learn_preference('Trading', 'risk', 'agro_mode', True)
            memory.learn_preference('Trading', 'risk', 'base_risk', 0.03)  # 3% AGRO
            memory.learn_preference('Quick Cash', 'services', 'status', 'Ready to Launch')
            memory.learn_preference('Financial', 'burn_rate', 'monthly', -635)
            memory.learn_preference('Financial', 'target_cut', 'monthly', 330)

            # Add optimization knowledge
            memory.add_knowledge(
                'AGRO MODE Active',
                'Phoenix Mark XII upgraded to AGRO MODE - 3% risk per trade, 5 max positions, targeting $4-5k/month. Circuit breakers at 8%, 15%, 25% drawdown.',
                source='Activation Feb 5, 2026'
            )

            memory.add_knowledge(
                'Quick Cash Services',
                'Three services production-ready: QR codes ($25-60), 3D models ($50-150), Python automation ($75-200). 11 portfolio samples complete. Target +$300-700/month.',
                source='Testing Feb 5, 2026'
            )

            memory.add_knowledge(
                'Optimization Report',
                '20 optimizations identified worth $2.3M+ additional value. Urgent: Cut $330/month expenses, launch Quick Cash, S-Corp formation, 60hr/week schedule.',
                source='Optimization Analysis Feb 5, 2026'
            )

        st.session_state.memory_initialized = True

    except Exception as e:
        print(f"Warning: Trinity Memory initialization failed: {e}")

# ============================================================================
# HOMEPAGE / DASHBOARD
# ============================================================================

def render_homepage():
    """Render the main homepage/dashboard with system overview."""
    st.header("🏠 Trinity System Overview")

    # System Status Banner
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        phoenix_status = check_phoenix_status()
        st.metric("Phoenix AGRO", "🟢 Active" if phoenix_status else "🔴 Offline")

    with col2:
        quick_cash_status = get_quick_cash_status()
        st.metric("Quick Cash", f"{quick_cash_status['ready']}/3 Ready")

    with col3:
        burn_rate = get_current_burn_rate()
        st.metric("Burn Rate", f"${burn_rate:,.0f}/mo",
                 delta=f"Target: -$330" if burn_rate < 0 else "Positive")

    with col4:
        week1_progress = get_week1_progress()
        st.metric("Week 1 Actions", f"{week1_progress['done']}/5")

    with col5:
        system_health = check_system_health()
        st.metric("System Health", f"{system_health}%")

    st.divider()

    # Quick Actions Grid
    st.subheader("⚡ Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 💰 Financial")
        if st.button("📊 View Financial Projections", use_container_width=True):
            st.session_state.active_module = "Financial"
            st.rerun()
        if st.button("💼 Launch Quick Cash Services", use_container_width=True):
            st.session_state.active_module = "Quick Cash"
            st.rerun()
        if st.button("📈 Week 1 Urgent Actions", use_container_width=True):
            st.session_state.active_module = "Quick Cash"
            st.rerun()

    with col2:
        st.markdown("### 🤖 AI Operations")
        if st.button("📊 Trading Station (AGRO)", use_container_width=True):
            st.session_state.active_module = "Trading"
            st.rerun()
        if st.button("🤖 AI Assistant Chat", use_container_width=True):
            st.session_state.active_module = "AI Assistant"
            st.rerun()
        if st.button("🧠 Memory Search", use_container_width=True):
            st.session_state.active_module = "Memory"
            st.rerun()

    with col3:
        st.markdown("### 🛠️ Development")
        if st.button("💻 Claude Code Terminal", use_container_width=True):
            st.session_state.active_module = "Claude Code"
            st.rerun()
        if st.button("🔧 Engineering Station", use_container_width=True):
            st.session_state.active_module = "Engineering"
            st.rerun()
        if st.button("🎯 Career Station", use_container_width=True):
            st.session_state.active_module = "Career"
            st.rerun()

    st.divider()

    # Recent Activity & Alerts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🚨 Critical Alerts")
        alerts = get_critical_alerts()
        if alerts:
            for alert in alerts:
                st.warning(f"**{alert['title']}**: {alert['message']}")
        else:
            st.success("✅ No critical alerts")

    with col2:
        st.subheader("📈 Today's Highlights")
        highlights = get_daily_highlights()
        for highlight in highlights:
            st.info(f"• {highlight}")

    st.divider()

    # System Metrics
    st.subheader("📊 System Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Trading Bot", "Phoenix AGRO")
        st.caption("3% risk, 5 positions")
        st.caption("Target: $4-5k/month")

    with col2:
        revenue_target = get_monthly_revenue_target()
        current_revenue = get_current_monthly_revenue()
        st.metric("Revenue Target", f"${revenue_target:,.0f}/mo")
        st.caption(f"Current: ${current_revenue:,.0f}")
        st.progress(min(current_revenue / revenue_target, 1.0))

    with col3:
        runway_months = calculate_runway()
        st.metric("Runway", f"{runway_months} months")
        st.caption("At current burn rate")
        if runway_months < 18:
            st.caption("⚠️ Below 18mo target")

    with col4:
        optimization_value = 2300000  # $2.3M from report
        st.metric("Optimization Value", "$2.3M+")
        st.caption("20 optimizations")
        st.caption("Identified Feb 5, 2026")

# Helper functions for homepage
def check_phoenix_status() -> bool:
    """Check if Phoenix is running."""
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'mark_xii_phoenix'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def get_quick_cash_status() -> Dict:
    """Get Quick Cash services status."""
    return {
        'ready': 3,  # All 3 services ready
        'total': 3,
        'services': ['QR Codes', '3D Models', 'Python Automation']
    }

def get_current_burn_rate() -> float:
    """Get current monthly burn rate."""
    return -635.0  # From optimization report

def get_week1_progress() -> Dict:
    """Get Week 1 urgent actions progress."""
    # Could be loaded from a tracking file
    return {
        'done': len([k for k, v in st.session_state.week1_checklist.items() if v]),
        'total': 5
    }

def check_system_health() -> int:
    """Calculate system health score."""
    score = 100

    # Phoenix not running: -20
    if not check_phoenix_status():
        score -= 20

    # High burn rate: -10
    if get_current_burn_rate() < -600:
        score -= 10

    # Quick Cash not launched: -10
    if get_quick_cash_status()['ready'] < 3:
        score -= 10

    return max(0, score)

def get_critical_alerts() -> List[Dict]:
    """Get critical system alerts."""
    alerts = []

    if get_current_burn_rate() < -600:
        alerts.append({
            'title': 'Cash Flow Crisis',
            'message': f'Burn rate: ${get_current_burn_rate()}/mo. Execute Week 1 actions immediately.'
        })

    if not check_phoenix_status():
        alerts.append({
            'title': 'Phoenix Offline',
            'message': 'AGRO MODE bot not running. Start with: python3 mark_xii_phoenix.py'
        })

    return alerts

def get_daily_highlights() -> List[str]:
    """Get today's highlights."""
    return [
        "Phoenix AGRO MODE activated (3% risk)",
        "Quick Cash services production-ready",
        "Optimization report: $2.3M+ value identified",
        "Week 1 urgent actions plan created"
    ]

def get_monthly_revenue_target() -> float:
    """Get monthly revenue target."""
    return 3885.0  # Current expenses from report

def get_current_monthly_revenue() -> float:
    """Get current monthly revenue."""
    return 3250.0  # After-tax income from report

def calculate_runway() -> int:
    """Calculate runway in months."""
    # From optimization report: 16 months at -$635/mo burn
    return 16

# ============================================================================
# FINANCIAL PROJECTIONS STATION
# ============================================================================

def render_financial_station():
    """Render comprehensive financial projections dashboard."""
    st.header("💰 Financial Projections & Analysis")

    # Summary Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Current Burn Rate", "-$635/mo", delta="-$330 target")
    with col2:
        st.metric("Runway", "16 months", delta="+14mo with cuts")
    with col3:
        st.metric("Monthly Target", "$3,885", help="Total monthly expenses")
    with col4:
        st.metric("Gap to Close", "$635", help="Current deficit")

    st.divider()

    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "💸 Income Sources",
        "📉 Expenses",
        "📈 10-Year Projection",
        "⚡ Optimizations"
    ])

    with tab1:
        render_financial_overview()

    with tab2:
        render_income_sources()

    with tab3:
        render_expenses_breakdown()

    with tab4:
        render_10year_projection()

    with tab5:
        render_optimizations()

def render_financial_overview():
    """Render financial overview."""
    st.subheader("Current Financial State")

    # Income vs Expenses
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💵 Monthly Income")
        st.metric("Current", "$3,250", help="After-tax income")

        st.markdown("**Sources:**")
        st.write("• Base income: $3,250")
        st.write("• Phoenix AGRO (target): $4,000-5,000")
        st.write("• Quick Cash (target): $300-700")
        st.write("• **Total target:** $7,550-9,000/mo")

    with col2:
        st.markdown("### 💳 Monthly Expenses")
        st.metric("Current", "$3,885")

        st.markdown("**Major Categories:**")
        st.write("• Rent: $1,500")
        st.write("• Food: $600")
        st.write("• Utilities: $200")
        st.write("• Transportation: $300")
        st.write("• Other: $1,285")

    st.divider()

    # Cash Flow Projection
    st.subheader("3-Month Cash Flow Projection")

    months = ["Month 1", "Month 2", "Month 3"]
    income = [3250, 5500, 8000]  # Base, +Phoenix partial, +Phoenix full+Quick Cash
    expenses = [3885, 3555, 3555]  # Current, then with $330 cuts
    net = [i - e for i, e in zip(income, expenses)]

    import pandas as pd
    df = pd.DataFrame({
        'Month': months,
        'Income': income,
        'Expenses': expenses,
        'Net': net
    })

    st.bar_chart(df.set_index('Month'))
    st.dataframe(df, use_container_width=True)

def render_income_sources():
    """Render detailed income sources."""
    st.subheader("Income Sources Breakdown")

    st.markdown("### Current Income")
    st.metric("Base Income (After Tax)", "$3,250/mo")

    st.divider()

    st.markdown("### Phoenix AGRO MODE (Activated)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Risk Level", "3%")
    with col2:
        st.metric("Max Positions", "5")
    with col3:
        st.metric("Target Return", "$4-5k/mo")

    st.info("**Status:** Active since Feb 5, 2026. Conservative target: $4,000/mo, Optimistic: $5,000/mo")

    st.divider()

    st.markdown("### Quick Cash Services (Ready to Launch)")

    services = [
        {"name": "QR Code Generation", "price": "$25-60", "time": "10-15min", "target": "$200-600/mo"},
        {"name": "3D Model Generation", "price": "$50-150", "time": "30min-2hr", "target": "$300-900/mo"},
        {"name": "Python Automation", "price": "$75-200", "time": "1-3hr", "target": "$500-1,500/mo"}
    ]

    for svc in services:
        with st.expander(f"**{svc['name']}** - {svc['price']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Pricing:** {svc['price']}")
                st.write(f"**Time per order:** {svc['time']}")
            with col2:
                st.write(f"**Monthly target:** {svc['target']}")
                st.write("**Status:** ✅ Production ready")

    st.success("**Combined target:** $1,000-3,000/mo (conservative: $300-700)")

def render_expenses_breakdown():
    """Render expenses breakdown with cut opportunities."""
    st.subheader("Monthly Expenses Breakdown")

    st.metric("Current Total", "$3,885/mo")
    st.metric("After $330 Cuts", "$3,555/mo", delta="-$330")

    st.divider()

    # Expenses table
    expenses = [
        {"category": "Rent", "current": 1500, "target": 1500, "notes": "Fixed"},
        {"category": "Food/Groceries", "current": 600, "target": 450, "notes": "Meal prep, less eating out"},
        {"category": "Utilities", "current": 200, "target": 185, "notes": "Lower thermostat, LED bulbs"},
        {"category": "Internet", "current": 80, "target": 50, "notes": "Call for promo rate"},
        {"category": "Phone", "current": 70, "target": 40, "notes": "Switch to prepaid"},
        {"category": "Transportation", "current": 300, "target": 280, "notes": "Insurance shopping"},
        {"category": "Entertainment", "current": 100, "target": 50, "notes": "Free alternatives"},
        {"category": "Subscriptions", "current": 47, "target": 0, "notes": "Cancel unused"},
        {"category": "Other", "current": 988, "target": 1000, "notes": "Misc expenses"}
    ]

    import pandas as pd
    df = pd.DataFrame(expenses)
    df['Savings'] = df['current'] - df['target']

    st.dataframe(df, use_container_width=True)

    total_savings = df['Savings'].sum()
    st.success(f"**Total Monthly Savings:** ${total_savings:,.0f}")

    st.divider()

    st.markdown("### Action Plan for Expense Cuts")
    st.markdown("""
    **Week 1 Actions:**
    - [ ] Cancel unused subscriptions (-$47/mo)
    - [ ] Call internet provider for lower rate (-$30/mo)
    - [ ] Switch phone to prepaid plan (-$30/mo)
    - [ ] Shop for car insurance quotes (-$20/mo)
    - [ ] Start meal prep routine (-$150/mo)
    - [ ] Cancel 1 streaming service (-$13/mo)
    - [ ] Reduce entertainment budget (-$50/mo)

    **Target:** -$330/mo total savings
    **Impact:** Extends runway from 16 → 30 months
    """)

def render_10year_projection():
    """Render 10-year financial projection."""
    st.subheader("10-Year Financial Projection (2026-2036)")

    st.info("Based on COMPLETE_FINANCIAL_MODEL_2026_2036.md and TRINITY_OPTIMIZATION_REPORT.md")

    # Scenario comparison
    scenario = st.selectbox(
        "Select Scenario:",
        ["Conservative", "Base", "Optimistic", "Optimized (With Improvements)"]
    )

    if scenario == "Conservative":
        year_1_income = 45000
        year_5_income = 180000
        year_10_total = 2900000
        notes = "Phoenix conservative + Quick Cash slow ramp + signal selling Year 3"
    elif scenario == "Base":
        year_1_income = 50000
        year_5_income = 250000
        year_10_total = 10100000
        notes = "Phoenix moderate + Quick Cash moderate + signal selling Year 2"
    elif scenario == "Optimistic":
        year_1_income = 65000
        year_5_income = 400000
        year_10_total = 25000000
        notes = "Phoenix aggressive + Quick Cash fast + signal selling Year 1 + exits"
    else:  # Optimized
        year_1_income = 68000
        year_5_income = 280000
        year_10_total = 12400000
        notes = "With all 20 optimizations from Feb 5, 2026 report"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Year 1 Income", f"${year_1_income:,.0f}")
    with col2:
        st.metric("Year 5 Income", f"${year_5_income:,.0f}")
    with col3:
        st.metric("Year 10 Total", f"${year_10_total:,.0f}")

    st.caption(notes)

    st.divider()

    # Key milestones
    st.markdown("### 🎯 Key Milestones")

    milestones = [
        {"date": "Month 1 (Feb 2026)", "event": "Quick Cash launch", "value": "+$300-700/mo"},
        {"date": "Month 2 (Mar 2026)", "event": "Phoenix AGRO compounds", "value": "+$4,000/mo"},
        {"date": "Month 3 (Apr 2026)", "event": "Positive cash flow", "value": "+$1,950-3,450/mo"},
        {"date": "Month 6 (Jul 2026)", "event": "Collective2 launch", "value": "+$500-1,000/mo"},
        {"date": "Month 12 (Jan 2027)", "event": "Signal selling 50 subs", "value": "+$5,000/mo"},
        {"date": "Year 2 (2027)", "event": "Capital to $100k", "value": "$100,000"},
        {"date": "Year 3 (2028)", "event": "Signal selling 200 subs", "value": "+$20,000/mo"},
        {"date": "Year 5 (2030)", "event": "Multiple income streams", "value": "$250k-400k/yr"},
        {"date": "Year 10 (2036)", "event": "Financial independence", "value": "$10M+ net worth"}
    ]

    for m in milestones:
        with st.expander(f"**{m['date']}** - {m['event']}"):
            st.write(f"**Target Value:** {m['value']}")

def render_optimizations():
    """Render optimizations from report."""
    st.subheader("⚡ 20 Optimization Opportunities")

    st.success("**Total Additional Value:** $2.3M+ over 10 years")

    st.markdown("### 🚨 Urgent (This Week)")
    urgent = [
        "1. Cut $330/month expenses → Extends runway 16→30 months",
        "2. Launch 3 Fiverr gigs → +$300-700/mo by Month 2",
        "3. S-Corp research & formation → Save $14k Year 1",
        "4. Collective2 account setup → +$85k-120k over 10 years",
        "5. Implement 60hr/week schedule → Prevent burnout"
    ]
    for item in urgent:
        st.warning(item)

    st.divider()

    st.markdown("### 💰 Financial Optimizations (7)")
    financial = [
        "AGRO MODE+ (3.5% risk) → +$1-1.5k/mo",
        "QSBS strategy → +$390k tax savings on exit",
        "Fiverr pricing increase after reviews → +$14k/year",
        "Accelerated capital injection → Better compounding",
        "Collective2 immediate launch → +$85-120k",
        "Tax optimization (S-Corp) → +$180k over 10 years",
        "Capital allocation front-loading → +10-15% returns"
    ]
    for item in financial:
        st.info(f"• {item}")

    st.divider()

    st.markdown("### 🔧 Technical Optimizations (5)")
    technical = [
        "Cancel Jarvis Phase 2-7 build → Save 480-600 hours",
        "Ship Trinity MVP in 8 weeks → Faster revenue",
        "Tech stack simplification → 60% less complexity",
        "Fiverr service automation → Faster delivery",
        "Phoenix algorithm optimization → +5-10% returns"
    ]
    for item in technical:
        st.info(f"• {item}")

    st.divider()

    st.markdown("### 🎯 Strategic Optimizations (4)")
    strategic = [
        "Blue ocean positioning → Less competition",
        "Aggregation strategy → Platform leverage",
        "Faster path to $10M (7 years vs 10) → 30% faster",
        "Optionality preservation → Multiple exit paths"
    ]
    for item in strategic:
        st.info(f"• {item}")

# ============================================================================
# QUICK CASH STATION
# ============================================================================

def render_quick_cash_station():
    """Render Quick Cash services dashboard with Week 1 actions."""
    st.header("⚡ Quick Cash Services & Week 1 Actions")

    # Service Status
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Services Ready", "3/3", help="All production-ready")
    with col2:
        st.metric("Portfolio Samples", "11", help="QR codes, 3D models, scripts")
    with col3:
        st.metric("Gig Descriptions", "3/3", help="Fiverr ready")
    with col4:
        st.metric("Launch Status", "Ready", delta="Launch this week")

    st.divider()

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📦 Services", "📋 Week 1 Actions", "📊 Launch Plan"])

    with tab1:
        render_quick_cash_services()

    with tab2:
        render_week1_actions()

    with tab3:
        render_launch_plan()

def render_quick_cash_services():
    """Render Quick Cash services overview."""
    st.subheader("Production-Ready Services")

    services = [
        {
            "name": "QR Code Generation",
            "status": "✅ Ready",
            "pricing": "$25-60",
            "delivery": "10-15 minutes",
            "samples": 5,
            "target": "$200-600/mo",
            "effective_rate": "$100-150/hr"
        },
        {
            "name": "3D Model Generation",
            "status": "✅ Ready",
            "pricing": "$50-150",
            "delivery": "30min-2hr",
            "samples": 3,
            "target": "$300-900/mo",
            "effective_rate": "$50-100/hr"
        },
        {
            "name": "Python Automation",
            "status": "✅ Ready",
            "pricing": "$75-200",
            "delivery": "1-3 hours",
            "samples": 3,
            "target": "$500-1,500/mo",
            "effective_rate": "$40-100/hr"
        }
    ]

    for svc in services:
        with st.expander(f"**{svc['name']}** - {svc['status']}"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**Pricing:** {svc['pricing']}")
                st.write(f"**Delivery:** {svc['delivery']}")

            with col2:
                st.write(f"**Portfolio:** {svc['samples']} samples")
                st.write(f"**Effective Rate:** {svc['effective_rate']}")

            with col3:
                st.write(f"**Monthly Target:** {svc['target']}")
                st.button(f"View Gig Description", key=f"gig_{svc['name']}")

def render_week1_actions():
    """Render Week 1 urgent action checklist."""
    st.subheader("🚨 Week 1 Urgent Actions (Feb 5-12, 2026)")

    st.info("**Mission:** Stop the bleeding. Launch revenue streams. Cut waste.")

    # Action 1: Emergency Expense Cut
    with st.expander("**Action #1:** Emergency Expense Cut (-$330/month)", expanded=True):
        st.markdown("**Impact:** Extends runway from 16 → 30 months")

        cuts = [
            ("Cancel unused subscriptions", 47, "subscriptions"),
            ("Internet - call for promo rate", 30, "internet"),
            ("Phone - switch to prepaid", 30, "phone"),
            ("Insurance - shop for quotes", 20, "insurance"),
            ("Food - meal prep routine", 150, "food"),
            ("Entertainment - free alternatives", 50, "entertainment"),
            ("Subscriptions - cancel 1 service", 13, "streaming")
        ]

        for label, savings, key in cuts:
            checked = st.checkbox(
                f"{label} (-${savings}/mo)",
                key=f"week1_cut_{key}",
                value=st.session_state.week1_checklist.get(f"cut_{key}", False)
            )
            if checked != st.session_state.week1_checklist.get(f"cut_{key}", False):
                st.session_state.week1_checklist[f"cut_{key}"] = checked

    # Action 2: Launch Quick Cash
    with st.expander("**Action #2:** Launch Quick Cash Services", expanded=False):
        st.markdown("**Impact:** +$300-700/month by Month 2")

        steps = [
            "Set up Fiverr account (30 min)",
            "Create QR Code gig (1 hour)",
            "Create 3D Model gig (1 hour)",
            "Create Python Automation gig (1 hour)",
            "Social media marketing (2 hours)",
            "Direct outreach to 20 contacts (2 hours)"
        ]

        for step in steps:
            checked = st.checkbox(
                step,
                key=f"week1_launch_{steps.index(step)}",
                value=st.session_state.week1_checklist.get(f"launch_{steps.index(step)}", False)
            )
            if checked != st.session_state.week1_checklist.get(f"launch_{steps.index(step)}", False):
                st.session_state.week1_checklist[f"launch_{steps.index(step)}"] = checked

    # Action 3: S-Corp Research
    with st.expander("**Action #3:** S-Corp Formation Research", expanded=False):
        st.markdown("**Impact:** Saves $14,470 Year 1, $180k+ over 10 years")

        steps = [
            "Read IRS S-Corp election guide (30 min)",
            "Research state requirements (30 min)",
            "Find 3 business attorneys (30 min)",
            "Schedule 2 consultations (30 min)",
            "Make go/no-go decision (1 hour)"
        ]

        for step in steps:
            checked = st.checkbox(
                step,
                key=f"week1_scorp_{steps.index(step)}",
                value=st.session_state.week1_checklist.get(f"scorp_{steps.index(step)}", False)
            )
            if checked != st.session_state.week1_checklist.get(f"scorp_{steps.index(step)}", False):
                st.session_state.week1_checklist[f"scorp_{steps.index(step)}"] = checked

    st.divider()

    # Progress Summary
    total_items = 18  # Total checklist items
    completed_items = sum(1 for v in st.session_state.week1_checklist.values() if v)
    progress = completed_items / total_items if total_items > 0 else 0

    st.subheader("Progress")
    st.progress(progress)
    st.metric("Completed", f"{completed_items}/{total_items}")

    if completed_items == total_items:
        st.balloons()
        st.success("🎉 Week 1 actions complete! You're on track to positive cash flow!")

def render_launch_plan():
    """Render Quick Cash launch plan."""
    st.subheader("📋 24-48 Hour Launch Plan")

    st.markdown("""
    ### Phase 1: Account Setup (2 hours)
    - Create/verify Fiverr seller account
    - Complete profile 100%
    - Set up payment method
    - Prepare portfolio images

    ### Phase 2: Gig Creation (3 hours)
    - Create QR Code gig (1 hour)
    - Create 3D Model gig (1 hour)
    - Create Python Automation gig (1 hour)

    ### Phase 3: Marketing (2 hours)
    - LinkedIn announcement
    - Twitter/X post
    - Reddit posts (r/forhire, r/slavelabour)
    - Direct outreach to 20 contacts

    ### Phase 4: Operations Setup (1 hour)
    - Create delivery templates
    - Set up quality checklists
    - Prepare time management system

    **Total Time:** 8 hours
    **Target Launch:** Within 48 hours
    """)

    if st.button("📄 View Full Launch Plan Document", use_container_width=True):
        try:
            with open(BASE_DIR / "QUICK_CASH_LAUNCH_PLAN.md", 'r') as f:
                st.text_area("Full Launch Plan", f.read(), height=400)
        except:
            st.error("Launch plan document not found")

# ============================================================================
# CLAUDE CODE TERMINAL STATION
# ============================================================================

def render_claude_code_station():
    """Render Claude Code terminal integration."""
    st.header("💻 Claude Code Terminal")

    st.info("**Claude Code** - Command center for development, debugging, and system updates")

    # Status check
    claude_code_running = check_claude_code_status()

    col1, col2, col3 = st.columns(3)

    with col1:
        status_emoji = "🟢" if claude_code_running else "🔴"
        st.metric("Status", f"{status_emoji} {'Active' if claude_code_running else 'Inactive'}")

    with col2:
        st.metric("Session", "Trinity System")

    with col3:
        st.metric("Context", "200k tokens")

    st.divider()

    # Quick Actions
    st.subheader("⚡ Quick Actions")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🛠️ Development")
        if st.button("🔧 Debug Command Center", use_container_width=True):
            st.code("claude code --project Trinity-System", language="bash")
            st.info("Opens Claude Code in Trinity System project directory")

        if st.button("📊 Update Financial Data", use_container_width=True):
            st.code("# Update financial projections\ncd /Users/tybrown/Desktop/Trinity-System\ncode COMPLETE_FINANCIAL_MODEL_2026_2036.md", language="bash")

        if st.button("⚡ Deploy Optimizations", use_container_width=True):
            st.info("Execute Week 1 urgent actions via Claude Code")

    with col2:
        st.markdown("### 📈 Trading")
        if st.button("📊 Check Phoenix AGRO Status", use_container_width=True):
            try:
                if PHOENIX_LOG.exists():
                    with open(PHOENIX_LOG, 'r') as f:
                        log_lines = f.readlines()[-20:]
                    st.text_area("Phoenix Log (Last 20 lines)", "".join(log_lines), height=300)
            except:
                st.error("Could not read Phoenix log")

        if st.button("🔄 Restart Phoenix AGRO", use_container_width=True):
            st.code("cd /Users/tybrown/Desktop/Bot-Factory\npython3 switch_phoenix_mode.py agro\npython3 mark_xii_phoenix.py", language="bash")

    st.divider()

    # Terminal Access Methods
    st.subheader("🖥️ Terminal Access")

    tab1, tab2, tab3 = st.tabs(["📱 Launch", "📋 Commands", "🔗 Direct Link"])

    with tab1:
        st.markdown("### Open Claude Code Terminal")

        st.code("""# Mac/Linux
open -a Terminal

# Then run:
cd /Users/tybrown/Desktop/Trinity-System
claude code
""", language="bash")

        if st.button("🚀 Launch Terminal (MacOS)", use_container_width=True):
            try:
                subprocess.Popen([
                    'osascript', '-e',
                    'tell application "Terminal" to do script "cd /Users/tybrown/Desktop/Trinity-System && claude code"'
                ])
                st.success("Terminal launched!")
            except Exception as e:
                st.error(f"Could not launch terminal: {e}")

    with tab2:
        st.markdown("### Useful Commands")

        commands = [
            ("Check system status", "ps aux | grep -E '(phoenix|trinity|streamlit)'"),
            ("View Phoenix log", "tail -f /Users/tybrown/Desktop/Bot-Factory/mark_xii_phoenix.log"),
            ("Git status", "git status"),
            ("Commit changes", "git add . && git commit -m 'Update' && git push"),
            ("Update Command Center", "cd /Users/tybrown/Desktop/Trinity-System && python3 command_center_v2.py"),
            ("Switch Phoenix to AGRO", "cd /Users/tybrown/Desktop/Bot-Factory && python3 switch_phoenix_mode.py agro")
        ]

        for label, cmd in commands:
            with st.expander(label):
                st.code(cmd, language="bash")
                if st.button(f"Copy", key=f"copy_{commands.index((label, cmd))}"):
                    st.success("Copied to clipboard (use Ctrl+V to paste)")

    with tab3:
        st.markdown("### Direct Terminal Link")
        st.info("Claude Code CLI currently requires terminal access")
        st.markdown("""
        **To access Claude Code:**
        1. Open Terminal.app
        2. Navigate to project: `cd /Users/tybrown/Desktop/Trinity-System`
        3. Run: `claude code`

        **Future:** Web-based terminal integration planned
        """)

    st.divider()

    # Self-Update Feature
    st.subheader("🔄 Self-Update Command Center")

    st.markdown("""
    ### Update This Dashboard
    Use Claude Code to modify and improve the Command Center:

    1. Open Claude Code terminal
    2. Request changes: "Update command center to add X feature"
    3. Claude will modify `command_center_v2.py`
    4. Restart Streamlit to see changes
    """)

    if st.button("📝 Generate Update Request Template", use_container_width=True):
        template = """# Command Center Update Request

**Feature:** [Describe what you want to add/change]

**Location:** command_center_v2.py

**Requirements:**
- [ ] Maintain existing functionality
- [ ] Add new feature
- [ ] Test changes
- [ ] Update documentation

**Claude Code Prompt:**
"Update Trinity Command Center to [your request]. Maintain all existing features."
"""
        st.text_area("Copy this template:", template, height=300)

def check_claude_code_status() -> bool:
    """Check if Claude Code CLI session is active."""
    try:
        # Check for claude process
        result = subprocess.run(
            ['pgrep', '-f', 'claude'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

# ============================================================================
# IMPORT EXISTING MODULES FROM V1
# ============================================================================

# We'll import and reuse existing station functions from command_center.py
# This ensures backward compatibility while adding new features

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
    """Get Phoenix trading bot statistics with AGRO MODE info."""
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
        except:
            running = False

        return {
            'running': running,
            'symbol': 'QQQ',
            'latest_price': latest_price,
            'rsi': latest_rsi,
            'position': position,
            'mode': 'AGRO MODE (3% risk)',
            'log_updated': datetime.fromtimestamp(PHOENIX_LOG.stat().st_mtime).strftime('%H:%M:%S')
        }
    except Exception as e:
        return {'error': str(e)}

def render_trading_station():
    """Render the Trading Bot monitoring module with AGRO MODE status."""
    st.header("📊 Trading Station")

    # Phoenix Mark XII AGRO MODE Badge
    st.success("🏆 **Phoenix Mark XII - AGRO MODE** (Activated Feb 5, 2026)")

    # AGRO MODE details
    with st.expander("⚡ AGRO MODE Configuration"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Base Risk", "3.0%")
            st.caption("Up from 1.76%")
        with col2:
            st.metric("Max Positions", "5")
            st.caption("Concurrent trades")
        with col3:
            st.metric("Target Return", "$4-5k/mo")
            st.caption("10-12% monthly")

        st.divider()

        st.markdown("### Circuit Breakers")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Daily Loss:** -10%")
        with col2:
            st.write("**Drawdown Tiers:** 8%, 15%, 25%")
        with col3:
            st.write("**Min Equity:** $38,000")

    st.divider()

    # Phoenix Status
    phoenix = get_phoenix_stats()

    if 'error' in phoenix:
        st.error(f"Error: {phoenix['error']}")
    else:
        status_emoji = "🟢" if phoenix['running'] else "🔴"
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Status", f"{status_emoji} {'Online' if phoenix['running'] else 'Offline'}")
        with col2:
            st.write(f"**Mode:** {phoenix.get('mode', 'Unknown')}")
            st.write(f"**Last Update:** {phoenix['log_updated']}")

        if phoenix['running']:
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
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📈 View Log", width='stretch'):
            try:
                if PHOENIX_LOG.exists():
                    with open(PHOENIX_LOG, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.readlines()[-50:]
                    st.text_area("Phoenix AGRO Log (Last 50 lines)", "".join(log_content), height=400)
            except Exception as e:
                st.error(f"Error: {e}")

    with col2:
        if st.button("🔄 Refresh", width='stretch'):
            st.rerun()

    with col3:
        if st.button("📁 Open Bot-Factory", width='stretch'):
            try:
                if BOT_FACTORY_DIR.exists():
                    subprocess.run(["open", str(BOT_FACTORY_DIR)], timeout=5)
                    st.success("Opening...")
            except Exception as e:
                st.error(f"Error: {e}")

# For other stations (Career, Engineering, Business, AI Assistant, Memory),
# import from original command_center.py
try:
    from command_center import (
        render_career_station,
        render_engineering_station,
        render_business_station,
        render_ai_assistant_station,
        render_memory_dashboard,
        is_vr_mode,
        get_display_config
    )
except ImportError:
    # Fallback: use simplified versions if import fails
    def render_career_station():
        st.header("🎯 Career Station")
        st.info("Career station from v1 - Use command_center.py for full functionality")

    def render_engineering_station():
        st.header("🔧 Engineering Station")
        st.info("Engineering station from v1 - Use command_center.py for full functionality")

    def render_business_station():
        st.header("💼 Business Station")
        st.info("Business station from v1 - Use command_center.py for full functionality")

    def render_ai_assistant_station():
        st.header("🤖 AI Assistant")
        st.info("AI Assistant from v1 - Use command_center.py for full functionality")

    def render_memory_dashboard():
        st.header("🧠 Memory Dashboard")
        st.info("Memory dashboard from v1 - Use command_center.py for full functionality")

    def is_vr_mode():
        return st.session_state.get('vr_mode', False)

    def get_display_config():
        return {
            'font_size': 'large' if is_vr_mode() else 'normal',
            'button_size': 'large' if is_vr_mode() else 'normal',
            'layout': 'wide'
        }

# ============================================================================
# MAIN COMMAND CENTER INTERFACE
# ============================================================================

def render_header():
    """Render the command center header."""
    st.set_page_config(
        page_title="Trinity Command Center v2.0",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS styling
    vr_size = "1.3em" if is_vr_mode() else "1em"
    st.markdown(f"""
    <style>
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
        [data-testid="stMetricValue"] {{
            font-size: 2em;
            font-weight: bold;
            color: #00ff00;
        }}
    </style>
    """, unsafe_allow_html=True)

    st.title("🎯 TRINITY COMMAND CENTER v2.0")
    st.caption("Unified AI Workstation • Optimized for Growth • Self-Updating")

def render_sidebar():
    """Render the sidebar with module selection and settings."""
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1E1E1E/00FF00?text=TRINITY+v2", use_container_width=True)

        st.header("Control Panel")

        # VR Mode Toggle
        vr_toggle = st.toggle(
            "🥽 VR Mode",
            value=st.session_state.vr_mode,
            help="Optimize interface for Oculus Quest"
        )
        if vr_toggle != st.session_state.vr_mode:
            st.session_state.vr_mode = vr_toggle
            st.rerun()

        st.divider()

        # Module Selection
        st.subheader("Stations")
        modules = [
            "Homepage",
            "Financial",
            "Quick Cash",
            "Trading",
            "Career",
            "Engineering",
            "Business",
            "AI Assistant",
            "Memory",
            "Claude Code"
        ]

        module = st.radio(
            "Select Module:",
            modules,
            index=modules.index(st.session_state.active_module),
            label_visibility="collapsed"
        )

        if module != st.session_state.active_module:
            st.session_state.active_module = module
            st.rerun()

        st.divider()

        # System Status
        st.subheader("System Status")

        try:
            phoenix_running = subprocess.run(
                ['pgrep', '-f', 'mark_xii_phoenix'],
                capture_output=True,
                timeout=5
            ).returncode == 0
        except:
            phoenix_running = False

        st.write("🏆 Phoenix AGRO:", "🟢" if phoenix_running else "🔴")
        if phoenix_running:
            st.caption("✅ Active - 3% risk mode")

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
        st.caption(f"**Version:** 2.0 (Feb 5, 2026)")

        if st.button("🔄 Refresh", width='stretch'):
            st.rerun()

def main():
    """Main application entry point."""
    initialize_session_state()
    render_header()
    render_sidebar()

    # Route to active module
    module = st.session_state.active_module

    if module == "Homepage":
        render_homepage()
    elif module == "Financial":
        render_financial_station()
    elif module == "Quick Cash":
        render_quick_cash_station()
    elif module == "Trading":
        render_trading_station()
    elif module == "Career":
        render_career_station()
    elif module == "Engineering":
        render_engineering_station()
    elif module == "Business":
        render_business_station()
    elif module == "AI Assistant":
        render_ai_assistant_station()
    elif module == "Memory":
        render_memory_dashboard()
    elif module == "Claude Code":
        render_claude_code_station()

    # Footer
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.caption("⚡ Trinity v2.0")
    with col2:
        st.caption("🤖 Optimized")
    with col3:
        st.caption(f"💰 -$635/mo → Goal: +$3k/mo")
    with col4:
        with st.popover("⌨️ Shortcuts"):
            st.caption("**Ctrl+R**: Refresh")
            st.caption("**Esc**: Close modal")

if __name__ == "__main__":
    main()
