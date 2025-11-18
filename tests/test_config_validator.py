"""
Tests for configuration validator
"""

import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config_validator import ConfigValidator


class TestConfigValidator:
    """Test configuration validation"""

    def test_validator_creation(self):
        """Test creating a validator instance"""
        validator = ConfigValidator()
        assert validator is not None
        assert isinstance(validator.errors, list)
        assert isinstance(validator.warnings, list)
        assert isinstance(validator.info, list)

    def test_empty_lists_on_init(self):
        """Test that error/warning/info lists start empty"""
        validator = ConfigValidator()
        assert len(validator.errors) == 0
        assert len(validator.warnings) == 0
        assert len(validator.info) == 0

    def test_validate_directories_creates_missing(self, tmp_path):
        """Test that validate_directories creates missing dirs"""
        validator = ConfigValidator()

        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            validator.validate_directories()

            # Check that directories were created
            assert Path('workspace').exists()
            assert Path('results').exists()
            assert Path('data').exists()
            assert Path('logs').exists()
            assert Path('task_configs').exists()

        finally:
            os.chdir(original_dir)


class TestProcessorConfigValidation:
    """Test processor config validation"""

    def test_missing_processor_config(self, tmp_path):
        """Test detection of missing processor_config.yaml"""
        validator = ConfigValidator()

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            validator.validate_processor_config()
            assert any('processor_config.yaml not found' in error for error in validator.errors)

        finally:
            os.chdir(original_dir)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
