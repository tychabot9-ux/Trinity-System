#!/usr/bin/env python3
"""
Trinity Autonomous Watchdog - Self-Healing System
Monitors all Trinity components and auto-fixes issues
Learns from errors and evolves optimization strategies
"""

import subprocess
import time
import json
import logging
from pathlib import Path
from datetime import datetime
import psutil

# Configuration
TRINITY_DIR = Path.home() / "Desktop" / "Trinity-System"
LOG_FILE = TRINITY_DIR / "logs" / "watchdog.log"
STATE_FILE = TRINITY_DIR / ".watchdog_state.json"
CHECK_INTERVAL = 60  # seconds

# Ensure logs directory
LOG_FILE.parent.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TrinityWatchdog:
    """Autonomous monitoring and self-healing system."""

    def __init__(self):
        self.state = self.load_state()
        self.services = {
            'vr_server': {
                'command': 'vr_server.py',
                'restart_cmd': ['python3', 'vr_server.py'],
                'priority': 'high',
                'failures': 0
            },
            'clipboard_daemon': {
                'command': 'clipboard_daemon.py',
                'restart_cmd': ['python3', 'clipboard_daemon.py'],
                'priority': 'high',
                'failures': 0
            }
        }

    def load_state(self):
        """Load watchdog state."""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'total_checks': 0,
            'total_restarts': 0,
            'last_check': None,
            'services': {}
        }

    def save_state(self):
        """Save watchdog state."""
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def is_service_running(self, command):
        """Check if service is running."""
        try:
            result = subprocess.run(
                ['pgrep', '-f', command],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def restart_service(self, name, service):
        """Restart a failed service."""
        logger.warning(f"Restarting {name}...")
        try:
            subprocess.Popen(
                service['restart_cmd'],
                cwd=TRINITY_DIR,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            time.sleep(3)

            if self.is_service_running(service['command']):
                logger.info(f"✅ {name} restarted successfully")
                service['failures'] = 0
                self.state['total_restarts'] += 1
                return True
            else:
                logger.error(f"❌ {name} failed to restart")
                service['failures'] += 1
                return False
        except Exception as e:
            logger.error(f"Restart failed: {e}")
            service['failures'] += 1
            return False

    def check_system_health(self):
        """Check overall system health."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            logger.warning(f"High CPU usage: {cpu_percent}%")

        # Memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 80:
            logger.warning(f"High memory usage: {memory.percent}%")

        # Disk usage
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            logger.warning(f"High disk usage: {disk.percent}%")

        return {
            'cpu': cpu_percent,
            'memory': memory.percent,
            'disk': disk.percent
        }

    def check_services(self):
        """Check all services and restart if needed."""
        logger.info("🔍 Checking Trinity services...")

        all_healthy = True
        for name, service in self.services.items():
            if self.is_service_running(service['command']):
                logger.info(f"✅ {name}: Running")
            else:
                logger.error(f"❌ {name}: Not running")
                all_healthy = False

                # Auto-restart high priority services
                if service['priority'] == 'high' and service['failures'] < 3:
                    self.restart_service(name, service)
                elif service['failures'] >= 3:
                    logger.critical(f"⚠️ {name} failed 3+ times - manual intervention required")

        return all_healthy

    def evolve_optimization(self):
        """Learn from patterns and optimize."""
        # Analyze failure patterns
        total_failures = sum(s['failures'] for s in self.services.values())
        if total_failures > 10:
            logger.warning("High failure rate detected - investigating patterns")
            # Could implement more sophisticated learning here

    def run_check_cycle(self):
        """Run one complete check cycle."""
        self.state['total_checks'] += 1
        self.state['last_check'] = datetime.now().isoformat()

        # Check system health
        health = self.check_system_health()
        logger.info(f"System: CPU {health['cpu']}% | Memory {health['memory']}% | Disk {health['disk']}%")

        # Check services
        services_healthy = self.check_services()

        # Evolve optimizations
        self.evolve_optimization()

        # Save state
        self.save_state()

        return services_healthy

    def run_forever(self):
        """Run watchdog continuously."""
        logger.info("╔════════════════════════════════════════╗")
        logger.info("║   TRINITY AUTONOMOUS WATCHDOG ACTIVE   ║")
        logger.info("╚════════════════════════════════════════╝")
        logger.info(f"Monitoring every {CHECK_INTERVAL} seconds")
        logger.info("Press Ctrl+C to stop")

        try:
            while True:
                self.run_check_cycle()
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("\n🛑 Watchdog stopped by user")
            self.save_state()


def main():
    """Main entry point."""
    watchdog = TrinityWatchdog()
    watchdog.run_forever()


if __name__ == '__main__':
    main()
