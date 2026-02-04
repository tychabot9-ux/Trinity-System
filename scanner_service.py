#!/usr/bin/env python3
"""
Trinity Job Scanner Service
Runs automated job board scans every 6 hours
Low CPU priority to protect trading bot
"""

import os
import psutil
import time
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv

# Set low CPU priority
p = psutil.Process(os.getpid())
p.nice(10)
print("📉 Scanner Service CPU Priority set to Low (Background Mode)")

load_dotenv()

from job_scanner import run_scheduled_scan

def main():
    """Main scheduler service"""
    print(f"\n{'='*70}")
    print(f"  TRINITY AUTO-SCANNER SERVICE")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    print(f"⏰ Scan Interval: Every 6 hours")
    print(f"🔄 First scan will run immediately")
    print(f"📉 CPU Priority: Low (nice 10)")
    print(f"{'='*70}\n")

    # Create scheduler
    scheduler = BackgroundScheduler()

    # Schedule scans every 6 hours
    scheduler.add_job(
        func=run_scheduled_scan,
        trigger=IntervalTrigger(hours=6),
        id='job_board_scan',
        name='Scan job boards',
        replace_existing=True
    )

    # Start scheduler
    scheduler.start()

    # Run first scan immediately
    print("🚀 Running initial scan...\n")
    run_scheduled_scan()

    print(f"\n✅ Scheduler active. Next scan in 6 hours.")
    print(f"Press Ctrl+C to stop\n")

    try:
        # Keep service running
        while True:
            time.sleep(60)  # Check every minute

    except (KeyboardInterrupt, SystemExit):
        print("\n\n🛑 Shutting down scanner service...")
        scheduler.shutdown()
        print("✅ Scanner service stopped\n")

if __name__ == "__main__":
    main()
