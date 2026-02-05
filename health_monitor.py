#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════╗
║              TRINITY HEALTH MONITOR                            ║
║           Autonomous System Health Monitoring                  ║
║                  v1.0 - February 2026                          ║
╚════════════════════════════════════════════════════════════════╝

Continuously monitors Trinity system health and auto-recovers from failures.
"""

import os
import sys
import time
import json
import socket
import sqlite3
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "logs" / "health_monitor.log"
HEALTH_STATUS_FILE = BASE_DIR / "health_status.json"

# Ensure log directory
LOG_FILE.parent.mkdir(exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TrinityHealthMonitor:
    """Autonomous health monitoring and recovery system."""

    def __init__(self):
        """Initialize health monitor."""
        logger.info("╔════════════════════════════════════════╗")
        logger.info("║    TRINITY HEALTH MONITOR v1.0         ║")
        logger.info("╚════════════════════════════════════════╝")

        self.services = {
            'vr_server': {
                'port': 8503,
                'process_name': 'vr_server.py',
                'restart_command': ['python3', str(BASE_DIR / 'vr_server.py')],
                'critical': True
            },
            'command_center': {
                'port': 8502,
                'process_name': 'command_center.py',
                'restart_command': ['streamlit', 'run', str(BASE_DIR / 'command_center.py'),
                                   '--server.port', '8502', '--server.headless', 'true'],
                'critical': True
            },
            'trinity_api': {
                'port': 8001,
                'process_name': 'main.py',
                'restart_command': ['python3', str(BASE_DIR / 'main.py')],
                'critical': False
            }
        }

        self.databases = {
            'memory': BASE_DIR / 'data' / 'trinity_memory.db',
            'jobs': BASE_DIR / 'job_logs' / 'job_status.db'
        }

        self.check_interval = 30  # seconds
        self.auto_restart = True
        self.restart_attempts = {}

        logger.info(f"Monitoring {len(self.services)} services")
        logger.info(f"Check interval: {self.check_interval}s")
        logger.info(f"Auto-restart: {'ENABLED' if self.auto_restart else 'DISABLED'}")

    def check_port(self, port: int) -> bool:
        """Check if a port is listening."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except:
            return False

    def check_process(self, process_name: str) -> bool:
        """Check if a process is running."""
        try:
            result = subprocess.run(
                ['pgrep', '-f', process_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def check_database(self, db_path: Path) -> Dict:
        """Check database health."""
        if not db_path.exists():
            return {
                'status': 'missing',
                'error': f'Database file not found: {db_path}'
            }

        try:
            conn = sqlite3.connect(str(db_path), timeout=5)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            conn.close()

            if result and result[0] == 'ok':
                return {
                    'status': 'healthy',
                    'size': db_path.stat().st_size,
                    'modified': datetime.fromtimestamp(db_path.stat().st_mtime).isoformat()
                }
            else:
                return {
                    'status': 'corrupted',
                    'error': 'Database integrity check failed'
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def restart_service(self, service_name: str, config: Dict) -> bool:
        """Attempt to restart a service."""
        # Track restart attempts
        if service_name not in self.restart_attempts:
            self.restart_attempts[service_name] = []

        # Prevent restart loops (max 3 attempts in 5 minutes)
        recent_attempts = [t for t in self.restart_attempts[service_name]
                          if time.time() - t < 300]

        if len(recent_attempts) >= 3:
            logger.error(f"❌ {service_name}: Too many restart attempts, giving up")
            return False

        logger.warning(f"🔄 Attempting to restart {service_name}...")

        try:
            # Record attempt
            self.restart_attempts[service_name].append(time.time())

            # Start process in background
            subprocess.Popen(
                config['restart_command'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            # Wait for service to come up
            time.sleep(5)

            # Verify restart
            if self.check_port(config['port']):
                logger.info(f"✅ {service_name} restarted successfully")
                return True
            else:
                logger.error(f"❌ {service_name} restart failed (port not listening)")
                return False

        except Exception as e:
            logger.error(f"❌ Error restarting {service_name}: {e}")
            return False

    def check_service_health(self, service_name: str, config: Dict) -> Dict:
        """Check health of a single service."""
        status = {
            'service': service_name,
            'timestamp': datetime.now().isoformat(),
            'port': config['port'],
            'critical': config['critical']
        }

        # Check port
        port_ok = self.check_port(config['port'])
        status['port_listening'] = port_ok

        # Check process
        process_ok = self.check_process(config['process_name'])
        status['process_running'] = process_ok

        # Overall health
        status['healthy'] = port_ok and process_ok

        # Recovery action
        if not status['healthy'] and config['critical'] and self.auto_restart:
            logger.warning(f"⚠️  {service_name} is down, attempting recovery...")
            status['recovery_attempted'] = True
            status['recovery_successful'] = self.restart_service(service_name, config)
        else:
            status['recovery_attempted'] = False

        return status

    def check_system_health(self) -> Dict:
        """Comprehensive system health check."""
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'databases': {},
            'overall_status': 'healthy'
        }

        # Check all services
        critical_down = []
        for service_name, config in self.services.items():
            status = self.check_service_health(service_name, config)
            health_report['services'][service_name] = status

            if config['critical'] and not status['healthy']:
                critical_down.append(service_name)

        # Check databases
        for db_name, db_path in self.databases.items():
            health_report['databases'][db_name] = self.check_database(db_path)

        # Overall status
        if critical_down:
            health_report['overall_status'] = 'degraded'
            health_report['critical_services_down'] = critical_down

        return health_report

    def save_health_status(self, health_report: Dict):
        """Save health status to file."""
        try:
            with open(HEALTH_STATUS_FILE, 'w') as f:
                json.dump(health_report, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save health status: {e}")

    def monitor_loop(self):
        """Main monitoring loop."""
        logger.info("🚀 Starting health monitoring...")
        logger.info(f"Press Ctrl+C to stop\n")

        check_count = 0

        try:
            while True:
                check_count += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"Health Check #{check_count} - {datetime.now().strftime('%H:%M:%S')}")
                logger.info(f"{'='*60}")

                # Run health check
                health_report = self.check_system_health()

                # Save status
                self.save_health_status(health_report)

                # Report status
                overall = health_report['overall_status']
                if overall == 'healthy':
                    logger.info("✅ System Status: HEALTHY")
                else:
                    logger.warning(f"⚠️  System Status: {overall.upper()}")
                    if 'critical_services_down' in health_report:
                        logger.warning(f"Critical services down: {', '.join(health_report['critical_services_down'])}")

                # Service details
                for service_name, status in health_report['services'].items():
                    emoji = "✅" if status['healthy'] else "❌"
                    logger.info(f"  {emoji} {service_name}: {'UP' if status['healthy'] else 'DOWN'}")

                # Database details
                for db_name, status in health_report['databases'].items():
                    emoji = "✅" if status['status'] == 'healthy' else "❌"
                    logger.info(f"  {emoji} {db_name} DB: {status['status'].upper()}")

                # Wait for next check
                logger.info(f"\nNext check in {self.check_interval}s...")
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("\n\n🛑 Health monitoring stopped by user")
            logger.info("Final health status saved to health_status.json")


def main():
    """Run health monitor."""
    monitor = TrinityHealthMonitor()
    monitor.monitor_loop()


if __name__ == '__main__':
    main()
