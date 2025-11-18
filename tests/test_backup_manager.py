"""
Tests for backup manager
"""

import pytest
import sys
import os
import sqlite3
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backup_manager import BackupManager


class TestBackupManager:
    """Test backup manager functionality"""

    def test_backup_manager_creation(self, tmp_path):
        """Test creating a backup manager instance"""
        backup_dir = tmp_path / ".backups"
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        manager = BackupManager(
            backup_dir=str(backup_dir),
            data_dir=str(data_dir)
        )

        assert manager is not None
        assert backup_dir.exists()

    def test_create_backup_with_database(self, tmp_path):
        """Test creating a backup with a database file"""
        backup_dir = tmp_path / ".backups"
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        # Create a test database
        db_path = data_dir / "test.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
        cursor.execute("INSERT INTO test (value) VALUES ('test_data')")
        conn.commit()
        conn.close()

        # Create backup
        manager = BackupManager(
            backup_dir=str(backup_dir),
            data_dir=str(data_dir)
        )

        backup_name = manager.create_backup(description="Test backup")

        assert backup_name is not None
        assert (backup_dir / backup_name).exists()
        assert (backup_dir / backup_name / "manifest.json").exists()

    def test_list_backups(self, tmp_path):
        """Test listing backups"""
        backup_dir = tmp_path / ".backups"
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        manager = BackupManager(
            backup_dir=str(backup_dir),
            data_dir=str(data_dir)
        )

        # Initially should be empty
        backups = manager.list_backups()
        assert len(backups) == 0

    def test_rotate_backups(self, tmp_path):
        """Test backup rotation"""
        backup_dir = tmp_path / ".backups"
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        # Set max backups to 2
        os.environ['MAX_BACKUPS'] = '2'

        manager = BackupManager(
            backup_dir=str(backup_dir),
            data_dir=str(data_dir)
        )

        # Create 3 backups
        for i in range(3):
            (backup_dir / f"backup_2025010{i+1}_120000").mkdir()
            manifest = backup_dir / f"backup_2025010{i+1}_120000" / "manifest.json"
            manifest.write_text('{"timestamp": "test"}')

        # Rotate should keep only 2 most recent
        manager.rotate_backups()

        remaining = list(backup_dir.glob("backup_*"))
        assert len(remaining) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
