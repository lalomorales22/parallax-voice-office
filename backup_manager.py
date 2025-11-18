#!/usr/bin/env python3
"""
Backup and Recovery Manager for Parallax Voice Office
Handles automated backups, rotation, and restoration of database and configuration files
"""

import os
import sys
import shutil
import sqlite3
import time
import json
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import gzip

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackupManager:
    """Manages database and configuration backups with rotation"""

    def __init__(self, backup_dir: str = ".backups", data_dir: str = "data"):
        self.backup_dir = Path(backup_dir)
        self.data_dir = Path(data_dir)
        self.backup_dir.mkdir(exist_ok=True)

        # Backup configuration
        self.max_backups = int(os.getenv('MAX_BACKUPS', '30'))  # Keep 30 days
        self.backup_interval = int(os.getenv('BACKUP_INTERVAL', '86400'))  # Daily
        self.compress_backups = os.getenv('COMPRESS_BACKUPS', 'true').lower() == 'true'

        logger.info(f"Backup Manager initialized: {self.backup_dir}")
        logger.info(f"Max backups: {self.max_backups}, Interval: {self.backup_interval}s")

    def create_backup(self, description: str = "") -> Optional[str]:
        """Create a new backup of database and configuration files"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)

            # Create manifest
            manifest = {
                "timestamp": timestamp,
                "description": description,
                "files": [],
                "database_stats": {}
            }

            # Backup database files
            db_files = list(self.data_dir.glob("*.db"))
            for db_file in db_files:
                if db_file.exists():
                    dest = backup_path / db_file.name

                    # Use SQLite backup API for database files
                    if db_file.suffix == '.db':
                        self._backup_database(str(db_file), str(dest))
                        manifest["database_stats"][db_file.name] = self._get_db_stats(str(db_file))
                    else:
                        shutil.copy2(db_file, dest)

                    # Compress if enabled
                    if self.compress_backups:
                        self._compress_file(dest)
                        manifest["files"].append(f"{db_file.name}.gz")
                    else:
                        manifest["files"].append(db_file.name)

            # Backup configuration files
            config_files = [
                'processor_config.yaml',
                'mcp_config.json',
                '.env'
            ]

            for config_file in config_files:
                src = Path(config_file)
                if src.exists():
                    dest = backup_path / src.name
                    shutil.copy2(src, dest)

                    if self.compress_backups:
                        self._compress_file(dest)
                        manifest["files"].append(f"{src.name}.gz")
                    else:
                        manifest["files"].append(src.name)

            # Save manifest
            manifest_path = backup_path / "manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)

            # Calculate backup size
            total_size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
            manifest["size_bytes"] = total_size

            # Update manifest with size
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)

            logger.info(f"Backup created: {backup_name} ({total_size / 1024 / 1024:.2f} MB)")
            return backup_name

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None

    def _backup_database(self, src_db: str, dest_db: str):
        """Backup SQLite database using proper backup API"""
        try:
            src_conn = sqlite3.connect(src_db)
            dest_conn = sqlite3.connect(dest_db)

            with dest_conn:
                src_conn.backup(dest_conn)

            src_conn.close()
            dest_conn.close()

        except Exception as e:
            logger.error(f"Database backup failed for {src_db}: {e}")
            # Fallback to file copy
            shutil.copy2(src_db, dest_db)

    def _compress_file(self, file_path: Path):
        """Compress a file using gzip"""
        try:
            with open(file_path, 'rb') as f_in:
                with gzip.open(f"{file_path}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Remove original file after compression
            file_path.unlink()

        except Exception as e:
            logger.error(f"Compression failed for {file_path}: {e}")

    def _decompress_file(self, gz_path: Path, dest_path: Path):
        """Decompress a gzip file"""
        try:
            with gzip.open(gz_path, 'rb') as f_in:
                with open(dest_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

        except Exception as e:
            logger.error(f"Decompression failed for {gz_path}: {e}")
            raise

    def _get_db_stats(self, db_path: str) -> Dict:
        """Get statistics about a database"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            stats = {}

            # Get table counts
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                stats[table_name] = count

            conn.close()
            return stats

        except Exception as e:
            logger.error(f"Failed to get DB stats for {db_path}: {e}")
            return {}

    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []

        for backup_dir in sorted(self.backup_dir.glob("backup_*"), reverse=True):
            manifest_path = backup_dir / "manifest.json"
            if manifest_path.exists():
                try:
                    with open(manifest_path) as f:
                        manifest = json.load(f)

                    backups.append({
                        "name": backup_dir.name,
                        "timestamp": manifest.get("timestamp"),
                        "description": manifest.get("description", ""),
                        "files": manifest.get("files", []),
                        "size_mb": manifest.get("size_bytes", 0) / 1024 / 1024
                    })

                except Exception as e:
                    logger.error(f"Failed to read manifest for {backup_dir}: {e}")

        return backups

    def restore_backup(self, backup_name: str, target_dir: str = None) -> bool:
        """Restore a backup"""
        try:
            backup_path = self.backup_dir / backup_name
            if not backup_path.exists():
                logger.error(f"Backup not found: {backup_name}")
                return False

            manifest_path = backup_path / "manifest.json"
            if not manifest_path.exists():
                logger.error(f"Manifest not found for backup: {backup_name}")
                return False

            with open(manifest_path) as f:
                manifest = json.load(f)

            # Determine target directory
            if target_dir is None:
                target_dir = self.data_dir
            else:
                target_dir = Path(target_dir)
                target_dir.mkdir(exist_ok=True)

            # Restore files
            for file_name in manifest.get("files", []):
                src = backup_path / file_name

                # Handle compressed files
                if file_name.endswith('.gz'):
                    original_name = file_name[:-3]
                    dest = target_dir / original_name if original_name.endswith('.db') else Path(original_name)
                    self._decompress_file(src, dest)
                else:
                    dest = target_dir / file_name if file_name.endswith('.db') else Path(file_name)
                    shutil.copy2(src, dest)

                logger.info(f"Restored: {file_name}")

            logger.info(f"Backup restored successfully: {backup_name}")
            return True

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False

    def rotate_backups(self):
        """Remove old backups beyond retention limit"""
        try:
            backups = sorted(self.backup_dir.glob("backup_*"))

            if len(backups) > self.max_backups:
                to_delete = backups[:len(backups) - self.max_backups]

                for backup in to_delete:
                    shutil.rmtree(backup)
                    logger.info(f"Deleted old backup: {backup.name}")

                logger.info(f"Rotation complete: kept {self.max_backups} most recent backups")

        except Exception as e:
            logger.error(f"Rotation failed: {e}")

    def run_scheduled_backup(self):
        """Run backup on schedule (for Docker/background service)"""
        logger.info("Starting scheduled backup service")

        while True:
            try:
                logger.info("Creating scheduled backup...")
                backup_name = self.create_backup(description="Scheduled automatic backup")

                if backup_name:
                    self.rotate_backups()

                logger.info(f"Next backup in {self.backup_interval} seconds")
                time.sleep(self.backup_interval)

            except KeyboardInterrupt:
                logger.info("Backup service stopped")
                break
            except Exception as e:
                logger.error(f"Scheduled backup error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    parser = argparse.ArgumentParser(description="Parallax Voice Office Backup Manager")
    parser.add_argument('action', choices=['create', 'list', 'restore', 'rotate', 'scheduled'],
                       help='Action to perform')
    parser.add_argument('--name', help='Backup name (for restore)')
    parser.add_argument('--description', default='', help='Backup description')
    parser.add_argument('--target', help='Target directory for restore')
    parser.add_argument('--backup-dir', default='.backups', help='Backup directory')
    parser.add_argument('--data-dir', default='data', help='Data directory')

    args = parser.parse_args()

    manager = BackupManager(backup_dir=args.backup_dir, data_dir=args.data_dir)

    if args.action == 'create':
        backup_name = manager.create_backup(description=args.description)
        if backup_name:
            print(f"✓ Backup created: {backup_name}")
            sys.exit(0)
        else:
            print("✗ Backup failed")
            sys.exit(1)

    elif args.action == 'list':
        backups = manager.list_backups()
        if backups:
            print(f"\n{'Backup Name':<30} {'Date':<20} {'Size (MB)':<12} {'Description'}")
            print("-" * 90)
            for backup in backups:
                date = datetime.strptime(backup['timestamp'], '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
                print(f"{backup['name']:<30} {date:<20} {backup['size_mb']:<12.2f} {backup['description']}")
        else:
            print("No backups found")

    elif args.action == 'restore':
        if not args.name:
            print("Error: --name required for restore")
            sys.exit(1)

        success = manager.restore_backup(args.name, target_dir=args.target)
        if success:
            print(f"✓ Backup restored: {args.name}")
            sys.exit(0)
        else:
            print("✗ Restore failed")
            sys.exit(1)

    elif args.action == 'rotate':
        manager.rotate_backups()
        print("✓ Backup rotation complete")

    elif args.action == 'scheduled':
        manager.run_scheduled_backup()

if __name__ == '__main__':
    main()
