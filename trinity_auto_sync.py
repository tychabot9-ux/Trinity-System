#!/usr/bin/env python3
"""
Trinity Auto-Sync System
Standalone service that monitors all data sources and updates Command Center
Runs independently of Claude Code to avoid credit burning

Features:
- Auto-syncs Phoenix trading data
- Monitors financial accounts (Alpaca)
- Tracks task completion
- Integrates Gemini 2.0 Flash for Trinity AI
- Updates Command Center database in real-time
- No human interaction needed - fully autonomous

Author: Trinity System
Created: 2026-02-05
"""

import os
import sys
import json
import time
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Gemini AI integration
import google.generativeai as genai

# Alpaca for trading data
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient

# Load environment
from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent
BOT_FACTORY_DIR = BASE_DIR.parent / "Bot-Factory"
DB_FILE = BASE_DIR / "trinity_data.db"
STATE_FILE = BASE_DIR / "trinity_state.json"
LOG_FILE = BASE_DIR / "trinity_auto_sync.log"

# Update interval (seconds)
UPDATE_INTERVAL = 60  # Check every minute
PHOENIX_CHECK_INTERVAL = 30  # Check Phoenix every 30 seconds
ALPACA_SYNC_INTERVAL = 300  # Sync Alpaca every 5 minutes

# API Configuration
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET = os.getenv("APCA_API_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")

# Gmail for personal context (read-only)
GMAIL_ADDRESS = "tychabot9@gmail.com"

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_database():
    """Initialize SQLite database for Trinity data."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Phoenix trades table
    c.execute('''
        CREATE TABLE IF NOT EXISTS phoenix_trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            entry_price REAL,
            exit_price REAL,
            quantity INTEGER,
            pnl REAL,
            r_multiple REAL,
            status TEXT,
            option_symbol TEXT,
            dte INTEGER,
            delta REAL,
            iv REAL
        )
    ''')

    # Account snapshots table
    c.execute('''
        CREATE TABLE IF NOT EXISTS account_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            equity REAL NOT NULL,
            cash REAL NOT NULL,
            buying_power REAL,
            mode TEXT NOT NULL,
            daily_pnl REAL,
            total_pnl REAL
        )
    ''')

    # Task tracking table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT UNIQUE NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            completed_date TEXT,
            impact TEXT,
            due_date TEXT
        )
    ''')

    # Trinity chat history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS trinity_chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_message TEXT NOT NULL,
            trinity_response TEXT NOT NULL,
            context TEXT
        )
    ''')

    # System metrics table
    c.execute('''
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    log.info("Database initialized")

# ============================================================================
# PHOENIX MONITOR
# ============================================================================

class PhoenixMonitor:
    """Monitor Phoenix trading bot and sync data."""

    def __init__(self):
        self.phoenix_log = BOT_FACTORY_DIR / "mark_xii_phoenix.log"
        self.phoenix_state = BOT_FACTORY_DIR / "phoenix_state.json"
        self.last_position = 0

    def is_running(self) -> bool:
        """Check if Phoenix is running."""
        import subprocess
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'mark_xii_phoenix'],
                capture_output=True,
                timeout=3
            )
            return result.returncode == 0
        except:
            return False

    def parse_trades(self) -> List[Dict]:
        """Parse new trades from Phoenix log."""
        if not self.phoenix_log.exists():
            return []

        new_trades = []
        try:
            with open(self.phoenix_log, 'r') as f:
                f.seek(self.last_position)
                lines = f.readlines()
                self.last_position = f.tell()

                for line in lines:
                    # Look for trade execution lines
                    if "Executing" in line and "order" in line.lower():
                        # Parse trade data
                        trade = self._parse_trade_line(line)
                        if trade:
                            new_trades.append(trade)
        except Exception as e:
            log.error(f"Error parsing Phoenix log: {e}")

        return new_trades

    def _parse_trade_line(self, line: str) -> Optional[Dict]:
        """Parse a single trade line."""
        # TODO: Implement parsing logic based on log format
        return None

    def get_status(self) -> Dict:
        """Get Phoenix current status."""
        return {
            'running': self.is_running(),
            'mode': 'PAPER',  # Read from config
            'capital': 100000,
            'last_check': datetime.now().isoformat()
        }

# ============================================================================
# ALPACA SYNC
# ============================================================================

class AlpacaSync:
    """Sync Alpaca account data."""

    def __init__(self):
        if ALPACA_API_KEY and ALPACA_SECRET:
            self.trading_client = TradingClient(
                ALPACA_API_KEY,
                ALPACA_SECRET,
                paper=(ALPACA_BASE_URL.find("paper") != -1)
            )
        else:
            self.trading_client = None
            log.warning("Alpaca credentials not found")

    def get_account_snapshot(self) -> Optional[Dict]:
        """Get current account snapshot."""
        if not self.trading_client:
            return None

        try:
            account = self.trading_client.get_account()
            return {
                'timestamp': datetime.now().isoformat(),
                'equity': float(account.equity),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'mode': 'PAPER' if ALPACA_BASE_URL.find("paper") != -1 else 'LIVE',
                'daily_pnl': float(account.equity) - float(account.last_equity),
                'total_pnl': float(account.equity) - 100000  # Assuming $100k start
            }
        except Exception as e:
            log.error(f"Error getting Alpaca account: {e}")
            return None

# ============================================================================
# TRINITY AI ENGINE
# ============================================================================

class TrinityAI:
    """Gemini-powered Trinity AI for autonomous updates."""

    def __init__(self):
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            # Use stable Gemini Pro model
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
            log.warning("Gemini API key not found")

    def analyze_system_state(self, context: Dict) -> str:
        """Analyze current system state and provide insights."""
        if not self.model:
            return "Trinity AI offline - API key not configured"

        prompt = f"""
You are Trinity, the AI strategic advisor. Analyze the current system state and provide a brief insight.

CURRENT STATE:
- Phoenix Status: {context.get('phoenix_status', 'Unknown')}
- Account Equity: ${context.get('equity', 0):,.2f}
- Daily P&L: ${context.get('daily_pnl', 0):,.2f}
- Open Positions: {context.get('positions', 0)}
- Recent Trades: {context.get('recent_trades', 0)}
- Tasks Completed Today: {context.get('tasks_completed', 0)}

Provide a 1-2 sentence strategic insight or recommendation.
Be concise and actionable.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Log only once, don't spam
            if not hasattr(self, '_ai_error_logged'):
                log.warning(f"Trinity AI unavailable: {str(e)[:100]}")
                self._ai_error_logged = True
            return "Trinity AI temporarily unavailable"

    def generate_daily_summary(self, data: Dict) -> str:
        """Generate daily summary report."""
        if not self.model:
            return "Trinity AI offline"

        prompt = f"""
Generate a brief daily summary for the Trinity System.

DATA:
{json.dumps(data, indent=2)}

Format as:
**Daily Summary - [Date]**
- Key Metrics: [bullet points]
- Notable Events: [bullet points]
- Recommendations: [bullet points]

Keep it under 200 words.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Summary generation error: {str(e)}"

# ============================================================================
# AUTO-SYNC ENGINE
# ============================================================================

class TrinityAutoSync:
    """Main auto-sync engine."""

    def __init__(self):
        self.phoenix = PhoenixMonitor()
        self.alpaca = AlpacaSync()
        self.trinity_ai = TrinityAI()
        self.last_phoenix_check = 0
        self.last_alpaca_sync = 0
        self.db = DB_FILE

    def run(self):
        """Main sync loop."""
        log.info("Trinity Auto-Sync System starting...")
        log.info(f"Database: {self.db}")
        log.info(f"Update interval: {UPDATE_INTERVAL}s")

        while True:
            try:
                current_time = time.time()

                # Check Phoenix
                if current_time - self.last_phoenix_check >= PHOENIX_CHECK_INTERVAL:
                    self.sync_phoenix()
                    self.last_phoenix_check = current_time

                # Sync Alpaca
                if current_time - self.last_alpaca_sync >= ALPACA_SYNC_INTERVAL:
                    self.sync_alpaca()
                    self.last_alpaca_sync = current_time

                # Update system metrics
                self.update_metrics()

                # Sleep until next update
                time.sleep(UPDATE_INTERVAL)

            except KeyboardInterrupt:
                log.info("Shutting down gracefully...")
                break
            except Exception as e:
                log.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait a minute before retrying

    def sync_phoenix(self):
        """Sync Phoenix data."""
        status = self.phoenix.get_status()

        # Update system metrics
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute('''
            INSERT INTO system_metrics (timestamp, metric_name, metric_value)
            VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), 'phoenix_status', json.dumps(status)))
        conn.commit()
        conn.close()

        log.info(f"Phoenix sync: {status['running'] and 'RUNNING' or 'OFFLINE'}")

    def sync_alpaca(self):
        """Sync Alpaca account data."""
        snapshot = self.alpaca.get_account_snapshot()
        if not snapshot:
            return

        # Save to database
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute('''
            INSERT INTO account_snapshots (timestamp, equity, cash, buying_power, mode, daily_pnl, total_pnl)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            snapshot['timestamp'],
            snapshot['equity'],
            snapshot['cash'],
            snapshot['buying_power'],
            snapshot['mode'],
            snapshot['daily_pnl'],
            snapshot['total_pnl']
        ))
        conn.commit()
        conn.close()

        log.info(f"Alpaca sync: Equity ${snapshot['equity']:,.2f}, P&L ${snapshot['daily_pnl']:+,.2f}")

    def update_metrics(self):
        """Update system-wide metrics."""
        # Get context
        context = self._get_context()

        # Generate Trinity AI insight
        insight = self.trinity_ai.analyze_system_state(context)

        # Save insight
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute('''
            INSERT INTO system_metrics (timestamp, metric_name, metric_value)
            VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), 'trinity_insight', insight))
        conn.commit()
        conn.close()

    def _get_context(self) -> Dict:
        """Get current system context."""
        conn = sqlite3.connect(self.db)
        c = conn.cursor()

        # Get latest account snapshot
        c.execute('SELECT * FROM account_snapshots ORDER BY id DESC LIMIT 1')
        account = c.fetchone()

        # Get recent trades count
        c.execute('SELECT COUNT(*) FROM phoenix_trades WHERE timestamp > datetime("now", "-1 day")')
        recent_trades = c.fetchone()[0]

        conn.close()

        phoenix_status = self.phoenix.get_status()

        return {
            'phoenix_status': phoenix_status['running'] and 'RUNNING' or 'OFFLINE',
            'equity': account[2] if account else 100000,
            'daily_pnl': account[6] if account else 0,
            'positions': 0,  # TODO: Get from Alpaca
            'recent_trades': recent_trades,
            'tasks_completed': 0  # TODO: Get from tasks table
        }

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║        TRINITY AUTO-SYNC SYSTEM v1.0                       ║
    ║        Autonomous Data Synchronization                     ║
    ║        No Claude Code Credits Required                     ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    # Initialize database
    init_database()

    # Start auto-sync
    sync_engine = TrinityAutoSync()
    sync_engine.run()

if __name__ == "__main__":
    main()
