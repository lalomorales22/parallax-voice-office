#!/usr/bin/env python3
"""
Database Optimization and Cleanup for Parallax Voice Office
Provides database maintenance, cleanup, and performance optimization
"""

import os
import sys
import sqlite3
import logging
import argparse
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Handles database optimization and cleanup tasks"""

    def __init__(self, db_path: str = "data/task_processor.db"):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            logger.error(f"Database not found: {self.db_path}")
            sys.exit(1)

        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection failed: {e}")
            sys.exit(1)

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def analyze_database(self) -> Dict:
        """Analyze database and return statistics"""
        logger.info("\n" + "="*70)
        logger.info("Database Analysis")
        logger.info("="*70)

        stats = {}

        # Get database size
        db_size = self.db_path.stat().st_size
        stats['size_mb'] = db_size / 1024 / 1024
        logger.info(f"\nDatabase Size: {stats['size_mb']:.2f} MB")

        # Get table statistics
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.cursor.fetchall()

        logger.info(f"\nTables ({len(tables)}):")
        logger.info(f"{'Table Name':<30} {'Row Count':<15} {'Size Estimate':<15}")
        logger.info("-" * 60)

        stats['tables'] = {}
        for table in tables:
            table_name = table[0]

            # Get row count
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = self.cursor.fetchone()[0]

            # Estimate size
            self.cursor.execute(f"SELECT SUM(length(quote(value))) FROM {table_name}")
            size_estimate = self.cursor.fetchone()[0] or 0

            stats['tables'][table_name] = {
                'rows': row_count,
                'size_bytes': size_estimate
            }

            logger.info(f"{table_name:<30} {row_count:<15} {size_estimate/1024:.2f} KB")

        # Check for indexes
        self.cursor.execute("""
            SELECT name, tbl_name FROM sqlite_master
            WHERE type='index' AND sql IS NOT NULL
        """)
        indexes = self.cursor.fetchall()

        logger.info(f"\nIndexes ({len(indexes)}):")
        for idx in indexes:
            logger.info(f"  • {idx[0]} on {idx[1]}")

        stats['index_count'] = len(indexes)

        # Get task statistics if tasks table exists
        if 'tasks' in stats['tables']:
            logger.info("\nTask Statistics:")

            # Count by status
            self.cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
            status_counts = self.cursor.fetchall()
            for status, count in status_counts:
                logger.info(f"  {status}: {count}")

            # Find old completed tasks
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            self.cursor.execute(
                "SELECT COUNT(*) FROM tasks WHERE status='completed' AND created_at < ?",
                (thirty_days_ago,)
            )
            old_completed = self.cursor.fetchone()[0]
            stats['old_completed_tasks'] = old_completed

            if old_completed > 0:
                logger.info(f"\n  ⚠️  Found {old_completed} completed tasks older than 30 days")
                logger.info("     (Consider archiving with --cleanup-old)")

        logger.info("\n" + "="*70)

        return stats

    def vacuum_database(self):
        """Vacuum database to reclaim space and optimize"""
        logger.info("\nVacuuming database (this may take a while)...")

        try:
            # Get size before
            size_before = self.db_path.stat().st_size

            # Vacuum
            self.cursor.execute("VACUUM")
            self.conn.commit()

            # Get size after
            size_after = self.db_path.stat().st_size

            space_saved = size_before - size_after
            percent_saved = (space_saved / size_before * 100) if size_before > 0 else 0

            logger.info(f"✓ Vacuum complete")
            logger.info(f"  Before: {size_before/1024/1024:.2f} MB")
            logger.info(f"  After:  {size_after/1024/1024:.2f} MB")
            logger.info(f"  Saved:  {space_saved/1024/1024:.2f} MB ({percent_saved:.1f}%)")

        except sqlite3.Error as e:
            logger.error(f"Vacuum failed: {e}")

    def create_recommended_indexes(self):
        """Create recommended indexes for better performance"""
        logger.info("\nCreating recommended indexes...")

        indexes = [
            ("idx_tasks_status", "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)"),
            ("idx_tasks_created", "CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at DESC)"),
            ("idx_tasks_priority", "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)"),
            ("idx_tasks_scheduled", "CREATE INDEX IF NOT EXISTS idx_tasks_scheduled ON tasks(scheduled_time)"),
        ]

        created = 0
        for idx_name, sql in indexes:
            try:
                self.cursor.execute(sql)
                logger.info(f"  ✓ Created {idx_name}")
                created += 1
            except sqlite3.Error as e:
                logger.warning(f"  ⚠️  Failed to create {idx_name}: {e}")

        self.conn.commit()
        logger.info(f"✓ Created {created}/{len(indexes)} indexes")

    def cleanup_old_tasks(self, days: int = 30, keep_failed: bool = True):
        """Archive old completed tasks"""
        logger.info(f"\nCleaning up tasks older than {days} days...")

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Count tasks to be archived
        query = "SELECT COUNT(*) FROM tasks WHERE status='completed' AND created_at < ?"
        self.cursor.execute(query, (cutoff_date,))
        count = self.cursor.fetchone()[0]

        if count == 0:
            logger.info("  No old tasks to cleanup")
            return

        logger.info(f"  Found {count} old completed tasks")

        # Create archive directory
        archive_dir = Path(".deleted") / "archived_tasks"
        archive_dir.mkdir(parents=True, exist_ok=True)

        # Export tasks to JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_file = archive_dir / f"tasks_archive_{timestamp}.json"

        self.cursor.execute(
            "SELECT * FROM tasks WHERE status='completed' AND created_at < ?",
            (cutoff_date,)
        )

        import json

        tasks = []
        columns = [desc[0] for desc in self.cursor.description]
        for row in self.cursor.fetchall():
            task = dict(zip(columns, row))
            tasks.append(task)

        with open(archive_file, 'w') as f:
            json.dump(tasks, f, indent=2)

        logger.info(f"  ✓ Archived {len(tasks)} tasks to {archive_file}")

        # Delete from database
        self.cursor.execute(
            "DELETE FROM tasks WHERE status='completed' AND created_at < ?",
            (cutoff_date,)
        )
        self.conn.commit()

        logger.info(f"  ✓ Deleted {count} tasks from database")

    def optimize_database(self):
        """Run full optimization"""
        logger.info("\n" + "="*70)
        logger.info("Database Optimization")
        logger.info("="*70)

        # Create backup first
        logger.info("\nCreating backup...")
        backup_dir = Path(".backups")
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f"pre_optimization_{timestamp}.db"

        shutil.copy2(self.db_path, backup_path)
        logger.info(f"✓ Backup created: {backup_path}")

        # Run optimizations
        self.create_recommended_indexes()
        self.vacuum_database()

        # Analyze for query planner
        logger.info("\nUpdating query statistics...")
        self.cursor.execute("ANALYZE")
        self.conn.commit()
        logger.info("✓ Statistics updated")

        logger.info("\n" + "="*70)
        logger.info("✅ Optimization complete!")
        logger.info("="*70)

    def integrity_check(self) -> bool:
        """Check database integrity"""
        logger.info("\nRunning integrity check...")

        try:
            self.cursor.execute("PRAGMA integrity_check")
            result = self.cursor.fetchone()[0]

            if result == "ok":
                logger.info("✓ Database integrity check passed")
                return True
            else:
                logger.error(f"✗ Database integrity check failed: {result}")
                return False

        except sqlite3.Error as e:
            logger.error(f"Integrity check failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description="Database optimization and maintenance for Parallax Voice Office",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze database
  python db_optimizer.py --analyze

  # Run full optimization
  python db_optimizer.py --optimize

  # Clean up old tasks (archive and delete)
  python db_optimizer.py --cleanup-old --days 30

  # Create recommended indexes
  python db_optimizer.py --create-indexes

  # Vacuum database
  python db_optimizer.py --vacuum

  # Check integrity
  python db_optimizer.py --integrity-check
        """
    )

    parser.add_argument('--db-path', default='data/task_processor.db',
                       help='Path to database file')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze database and show statistics')
    parser.add_argument('--optimize', action='store_true',
                       help='Run full optimization (indexes + vacuum)')
    parser.add_argument('--vacuum', action='store_true',
                       help='Vacuum database to reclaim space')
    parser.add_argument('--create-indexes', action='store_true',
                       help='Create recommended indexes')
    parser.add_argument('--cleanup-old', action='store_true',
                       help='Archive and delete old completed tasks')
    parser.add_argument('--days', type=int, default=30,
                       help='Days threshold for cleanup (default: 30)')
    parser.add_argument('--integrity-check', action='store_true',
                       help='Check database integrity')

    args = parser.parse_args()

    # If no action specified, show help
    if not any([args.analyze, args.optimize, args.vacuum,
                args.create_indexes, args.cleanup_old, args.integrity_check]):
        parser.print_help()
        sys.exit(0)

    optimizer = DatabaseOptimizer(db_path=args.db_path)
    optimizer.connect()

    try:
        if args.integrity_check:
            if not optimizer.integrity_check():
                sys.exit(1)

        if args.analyze:
            optimizer.analyze_database()

        if args.create_indexes:
            optimizer.create_recommended_indexes()

        if args.vacuum:
            optimizer.vacuum_database()

        if args.cleanup_old:
            optimizer.cleanup_old_tasks(days=args.days)

        if args.optimize:
            optimizer.optimize_database()

    finally:
        optimizer.close()

    logger.info("\n✓ Done!")

if __name__ == '__main__':
    main()
