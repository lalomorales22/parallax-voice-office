"""
Tests for database optimizer
"""

import pytest
import sys
import os
import sqlite3
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db_optimizer import DatabaseOptimizer


class TestDatabaseOptimizer:
    """Test database optimizer functionality"""

    @pytest.fixture
    def test_db(self, tmp_path):
        """Create a test database"""
        db_path = tmp_path / "data"
        db_path.mkdir()
        db_file = db_path / "test.db"

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create a test table
        cursor.execute("""
            CREATE TABLE tasks (
                id TEXT PRIMARY KEY,
                status TEXT,
                created_at TEXT,
                priority TEXT
            )
        """)

        # Insert some test data
        from datetime import datetime, timedelta
        for i in range(100):
            date = datetime.now() - timedelta(days=i)
            cursor.execute("""
                INSERT INTO tasks (id, status, created_at, priority)
                VALUES (?, ?, ?, ?)
            """, (f"task_{i}", "completed", date.isoformat(), "medium"))

        conn.commit()
        conn.close()

        return db_file

    def test_optimizer_connection(self, test_db):
        """Test connecting to database"""
        optimizer = DatabaseOptimizer(db_path=str(test_db))
        optimizer.connect()
        assert optimizer.conn is not None
        optimizer.close()

    def test_analyze_database(self, test_db):
        """Test database analysis"""
        optimizer = DatabaseOptimizer(db_path=str(test_db))
        optimizer.connect()

        stats = optimizer.analyze_database()

        assert 'size_mb' in stats
        assert 'tables' in stats
        assert 'tasks' in stats['tables']
        assert stats['tables']['tasks']['rows'] == 100

        optimizer.close()

    def test_create_indexes(self, test_db):
        """Test index creation"""
        optimizer = DatabaseOptimizer(db_path=str(test_db))
        optimizer.connect()

        # Should create without errors
        optimizer.create_recommended_indexes()

        # Verify indexes were created
        optimizer.cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND name LIKE 'idx_tasks_%'
        """)

        indexes = optimizer.cursor.fetchall()
        assert len(indexes) > 0

        optimizer.close()

    def test_integrity_check(self, test_db):
        """Test database integrity check"""
        optimizer = DatabaseOptimizer(db_path=str(test_db))
        optimizer.connect()

        result = optimizer.integrity_check()
        assert result is True

        optimizer.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
