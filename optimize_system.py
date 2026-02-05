#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════╗
║              TRINITY SYSTEM OPTIMIZER                          ║
║           Automated Performance Optimization                   ║
║                  v1.0 - February 2026                          ║
╚════════════════════════════════════════════════════════════════╝

Automatically optimizes Trinity system for peak performance.
"""

import os
import sys
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Configuration
BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "logs" / "optimizer.log"

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


class TrinityOptimizer:
    """Automated system optimization."""

    def __init__(self):
        """Initialize optimizer."""
        logger.info("╔════════════════════════════════════════╗")
        logger.info("║    TRINITY SYSTEM OPTIMIZER v1.0       ║")
        logger.info("╚════════════════════════════════════════╝\n")

        self.optimizations_applied = []
        self.space_freed = 0
        self.performance_gain = 0

    def optimize_database(self, db_path: Path, db_name: str) -> bool:
        """Optimize SQLite database."""
        if not db_path.exists():
            logger.warning(f"⚠️  {db_name}: Database not found, skipping")
            return False

        try:
            logger.info(f"🔧 Optimizing {db_name} database...")

            # Get size before
            size_before = db_path.stat().st_size

            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # VACUUM to reclaim space
            cursor.execute("VACUUM")

            # ANALYZE to update statistics
            cursor.execute("ANALYZE")

            # Enable WAL mode for better concurrency
            cursor.execute("PRAGMA journal_mode=WAL")

            # Optimize page size
            cursor.execute("PRAGMA page_size=4096")

            # Increase cache size
            cursor.execute("PRAGMA cache_size=10000")

            conn.commit()
            conn.close()

            # Get size after
            size_after = db_path.stat().st_size
            space_saved = size_before - size_after

            if space_saved > 0:
                logger.info(f"  ✅ {db_name}: Optimized, freed {space_saved / 1024:.2f} KB")
                self.space_freed += space_saved
            else:
                logger.info(f"  ✅ {db_name}: Optimized (no space saved)")

            self.optimizations_applied.append(f"Database: {db_name}")
            return True

        except Exception as e:
            logger.error(f"  ❌ {db_name}: Optimization failed - {e}")
            return False

    def clean_old_cad_files(self, days: int = 30) -> int:
        """Clean old CAD files."""
        logger.info(f"🧹 Cleaning CAD files older than {days} days...")

        cad_dir = BASE_DIR / "cad_output"
        if not cad_dir.exists():
            logger.info("  ℹ️  No CAD directory found")
            return 0

        cutoff_time = datetime.now().timestamp() - (days * 86400)
        files_removed = 0
        space_freed = 0

        for file in cad_dir.glob("*"):
            if file.is_file() and file.stat().st_mtime < cutoff_time:
                file_size = file.stat().st_size
                file.unlink()
                files_removed += 1
                space_freed += file_size

        if files_removed > 0:
            logger.info(f"  ✅ Removed {files_removed} old files, freed {space_freed / 1024 / 1024:.2f} MB")
            self.space_freed += space_freed
            self.optimizations_applied.append(f"CAD cleanup: {files_removed} files")
        else:
            logger.info("  ℹ️  No old files to clean")

        return files_removed

    def clean_log_files(self, days: int = 7) -> int:
        """Rotate and compress old log files."""
        logger.info(f"📝 Rotating log files older than {days} days...")

        log_dir = BASE_DIR / "logs"
        if not log_dir.exists():
            logger.info("  ℹ️  No log directory found")
            return 0

        cutoff_time = datetime.now().timestamp() - (days * 86400)
        files_rotated = 0

        for log_file in log_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                # Archive old logs
                archive_name = log_file.with_suffix(f'.log.{datetime.now().strftime("%Y%m%d")}')
                log_file.rename(archive_name)
                files_rotated += 1

        if files_rotated > 0:
            logger.info(f"  ✅ Rotated {files_rotated} log files")
            self.optimizations_applied.append(f"Log rotation: {files_rotated} files")
        else:
            logger.info("  ℹ️  No logs to rotate")

        return files_rotated

    def optimize_python_cache(self) -> bool:
        """Clean Python cache files."""
        logger.info("🐍 Cleaning Python cache...")

        cache_dirs = list(BASE_DIR.rglob("__pycache__"))
        pyc_files = list(BASE_DIR.rglob("*.pyc"))

        total_removed = 0

        # Remove __pycache__ directories
        for cache_dir in cache_dirs:
            try:
                shutil.rmtree(cache_dir)
                total_removed += 1
            except:
                pass

        # Remove .pyc files
        for pyc_file in pyc_files:
            try:
                pyc_file.unlink()
                total_removed += 1
            except:
                pass

        if total_removed > 0:
            logger.info(f"  ✅ Removed {total_removed} cache files")
            self.optimizations_applied.append(f"Python cache: {total_removed} items")
            return True
        else:
            logger.info("  ℹ️  No cache to clean")
            return False

    def optimize_memory_db(self) -> bool:
        """Optimize Trinity Memory database."""
        db_path = BASE_DIR / "data" / "trinity_memory.db"
        return self.optimize_database(db_path, "Trinity Memory")

    def optimize_job_db(self) -> bool:
        """Optimize Job Status database."""
        db_path = BASE_DIR / "job_logs" / "job_status.db"
        return self.optimize_database(db_path, "Job Status")

    def create_backup(self, db_path: Path) -> bool:
        """Create database backup."""
        if not db_path.exists():
            return False

        try:
            backup_dir = BASE_DIR / "backups"
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"{db_path.stem}_{timestamp}.db"

            shutil.copy2(db_path, backup_path)
            logger.info(f"  ✅ Backup created: {backup_path.name}")
            return True

        except Exception as e:
            logger.error(f"  ❌ Backup failed: {e}")
            return False

    def run_full_optimization(self):
        """Run complete system optimization."""
        logger.info("🚀 Starting full system optimization...\n")

        start_time = datetime.now()

        # Backup critical databases first
        logger.info("💾 Creating backups...")
        self.create_backup(BASE_DIR / "data" / "trinity_memory.db")
        self.create_backup(BASE_DIR / "job_logs" / "job_status.db")
        print()

        # Optimize databases
        self.optimize_memory_db()
        self.optimize_job_db()
        print()

        # Clean old files
        self.clean_old_cad_files(days=30)
        print()

        # Rotate logs
        self.clean_log_files(days=7)
        print()

        # Clean Python cache
        self.optimize_python_cache()
        print()

        # Generate report
        elapsed = (datetime.now() - start_time).total_seconds()

        logger.info("=" * 60)
        logger.info("OPTIMIZATION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total optimizations: {len(self.optimizations_applied)}")
        logger.info(f"Space freed: {self.space_freed / 1024 / 1024:.2f} MB")
        logger.info(f"Time elapsed: {elapsed:.2f}s")
        logger.info("")

        if self.optimizations_applied:
            logger.info("Optimizations applied:")
            for opt in self.optimizations_applied:
                logger.info(f"  • {opt}")
        else:
            logger.info("No optimizations needed - system already optimal!")

        logger.info("")
        logger.info("✅ Trinity system optimized and ready")


def main():
    """Run system optimizer."""
    optimizer = TrinityOptimizer()
    optimizer.run_full_optimization()


if __name__ == '__main__':
    main()
