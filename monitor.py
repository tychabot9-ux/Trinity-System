#!/usr/bin/env python3
"""
Trinity Monitor - Real-Time Dashboard & Kill Switch
Displays live status and provides emergency controls

Features:
- Live application count
- Rate limit status
- Recent applications log
- Kill switch toggle
- Email monitoring (future)
- Daily summary
"""

import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Import safety config
from safety_config import (
    check_rate_limit,
    is_kill_switch_active,
    activate_kill_switch,
    deactivate_kill_switch,
    load_blacklist,
    MAX_DAILY_APPLICATIONS,
    MAX_HOURLY_APPLICATIONS
)

# Paths
DB_PATH = Path(__file__).parent / "job_logs" / "applications.db"

# ============================================================================
# DATABASE QUERIES
# ============================================================================

def get_application_stats():
    """Get application statistics"""
    if not DB_PATH.exists():
        return {
            "total": 0,
            "today": 0,
            "this_week": 0,
            "this_month": 0
        }

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total
    cursor.execute("SELECT COUNT(*) FROM applications")
    total = cursor.fetchone()[0]

    # Today
    today = datetime.now().date()
    cursor.execute("SELECT COUNT(*) FROM applications WHERE DATE(applied_date) = ?", (today,))
    today_count = cursor.fetchone()[0]

    # This week
    week_ago = datetime.now() - timedelta(days=7)
    cursor.execute("SELECT COUNT(*) FROM applications WHERE applied_date > ?", (week_ago,))
    week_count = cursor.fetchone()[0]

    # This month
    month_ago = datetime.now() - timedelta(days=30)
    cursor.execute("SELECT COUNT(*) FROM applications WHERE applied_date > ?", (month_ago,))
    month_count = cursor.fetchone()[0]

    conn.close()

    return {
        "total": total,
        "today": today_count,
        "this_week": week_count,
        "this_month": month_count
    }

def get_recent_applications(limit=10):
    """Get recent applications"""
    if not DB_PATH.exists():
        return []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT company, position, applied_date, fit_score, status
        FROM applications
        ORDER BY applied_date DESC
        LIMIT ?
    """, (limit,))

    results = cursor.fetchall()
    conn.close()

    return [
        {
            "company": r[0],
            "position": r[1],
            "date": r[2],
            "fit_score": r[3],
            "status": r[4]
        }
        for r in results
    ]

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_header():
    """Display dashboard header"""
    print("\n" + "="*70)
    print("  TRINITY SYSTEM - LIVE MONITOR")
    print("="*70)
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Mode: FULL-AUTO (Enhanced Safety)")
    print("="*70)

def display_status():
    """Display system status"""
    print("\n📊 SYSTEM STATUS:")

    # Kill Switch
    kill_switch = is_kill_switch_active()
    kill_status = "🚨 ACTIVE" if kill_switch else "✅ Inactive"
    print(f"  Kill Switch: {kill_status}")

    # Rate Limits
    rate = check_rate_limit()
    hourly_color = "🔴" if rate['hourly_count'] >= MAX_HOURLY_APPLICATIONS else "🟢"
    daily_color = "🔴" if rate['daily_count'] >= MAX_DAILY_APPLICATIONS else "🟢"

    print(f"  Hourly Limit: {hourly_color} {rate['hourly_count']}/{MAX_HOURLY_APPLICATIONS}")
    print(f"  Daily Limit: {daily_color} {rate['daily_count']}/{MAX_DAILY_APPLICATIONS}")

    # Blacklist
    blacklist = load_blacklist()
    print(f"  Blacklist: {len(blacklist)} companies")

def display_stats():
    """Display application statistics"""
    print("\n📈 APPLICATION STATS:")

    stats = get_application_stats()
    print(f"  Total Applications: {stats['total']}")
    print(f"  Today: {stats['today']}")
    print(f"  This Week: {stats['this_week']}")
    print(f"  This Month: {stats['this_month']}")

def display_recent():
    """Display recent applications"""
    print("\n📋 RECENT APPLICATIONS:")

    recent = get_recent_applications(5)

    if not recent:
        print("  No applications yet")
        return

    for app in recent:
        date = datetime.fromisoformat(app['date']).strftime('%m/%d %H:%M')
        print(f"  [{date}] {app['company']} - {app['position']}")
        print(f"           Fit: {app['fit_score']}/100 | Status: {app['status']}")

def display_menu():
    """Display control menu"""
    print("\n🎛️  CONTROLS:")
    print("  [K] Toggle Kill Switch")
    print("  [R] Refresh Display")
    print("  [L] View Full Log")
    print("  [B] View Blacklist")
    print("  [Q] Quit")

# ============================================================================
# INTERACTIVE CONTROLS
# ============================================================================

def toggle_kill_switch():
    """Toggle kill switch on/off"""
    if is_kill_switch_active():
        deactivate_kill_switch()
        print("\n  ✅ Kill switch DEACTIVATED - Applications resumed")

        # Send notification
        try:
            bot_factory = Path.home() / "Desktop" / "Bot-Factory"
            sys.path.insert(0, str(bot_factory))
            from notify import push_notification
            push_notification(
                "✅ Trinity Resumed",
                "Kill switch deactivated. Applications will resume.",
                sound="magic"
            )
        except:
            pass
    else:
        activate_kill_switch("Manual toggle from monitor")
        print("\n  🚨 Kill switch ACTIVATED - All applications stopped")

def view_full_log():
    """View complete application log"""
    print("\n" + "="*70)
    print("  COMPLETE APPLICATION LOG")
    print("="*70)

    apps = get_recent_applications(50)

    for i, app in enumerate(apps, 1):
        date = datetime.fromisoformat(app['date']).strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n{i}. {app['company']} - {app['position']}")
        print(f"   Date: {date}")
        print(f"   Fit Score: {app['fit_score']}/100")
        print(f"   Status: {app['status']}")

    print("\n" + "="*70)
    input("\nPress Enter to return...")

def view_blacklist():
    """View blacklisted companies"""
    print("\n" + "="*70)
    print("  BLACKLISTED COMPANIES")
    print("="*70)

    blacklist = load_blacklist()

    if not blacklist:
        print("\n  No companies blacklisted")
    else:
        for i, company in enumerate(blacklist, 1):
            print(f"  {i}. {company}")

    print("\n" + "="*70)
    input("\nPress Enter to return...")

def run_monitor():
    """Run interactive monitor"""
    while True:
        # Clear screen (works on Unix-like systems)
        os.system('clear' if os.name == 'posix' else 'cls')

        # Display dashboard
        display_header()
        display_status()
        display_stats()
        display_recent()
        display_menu()

        # Get user input
        choice = input("\n  Enter command: ").strip().upper()

        if choice == 'K':
            toggle_kill_switch()
            input("\nPress Enter to continue...")
        elif choice == 'R':
            continue  # Refresh
        elif choice == 'L':
            view_full_log()
        elif choice == 'B':
            view_blacklist()
        elif choice == 'Q':
            print("\n  Exiting monitor...")
            break
        else:
            print("\n  Invalid command")
            input("\nPress Enter to continue...")

# ============================================================================
# QUICK STATUS (Non-Interactive)
# ============================================================================

def quick_status():
    """Display quick status summary"""
    display_header()
    display_status()
    display_stats()
    display_recent()
    print("\n" + "="*70)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_status()
    else:
        try:
            run_monitor()
        except KeyboardInterrupt:
            print("\n\n  Monitor stopped")
