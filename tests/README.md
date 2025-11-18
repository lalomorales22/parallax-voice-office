# Parallax Voice Office - Test Suite

This directory contains the test suite for Parallax Voice Office.

## Running Tests

### Run all tests:
```bash
pytest tests/ -v
```

### Run specific test file:
```bash
pytest tests/test_config_validator.py -v
```

### Run with coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run in watch mode (requires pytest-watch):
```bash
ptw tests/
```

## Test Structure

- `test_config_validator.py` - Configuration validation tests
- `test_backup_manager.py` - Backup and recovery tests
- `test_db_optimizer.py` - Database optimization tests
- `test_mcp_integration.py` - MCP server integration tests (TODO)
- `test_api_endpoints.py` - API endpoint tests (TODO)
- `test_voice_interface.py` - Voice interface tests (TODO)

## Writing Tests

Tests use pytest framework. Follow these conventions:

1. Test files should start with `test_`
2. Test classes should start with `Test`
3. Test methods should start with `test_`
4. Use fixtures for setup/teardown
5. Use descriptive test names

Example:
```python
def test_feature_does_something():
    # Arrange
    input_data = "test"

    # Act
    result = process(input_data)

    # Assert
    assert result == expected_output
```

## Test Requirements

Install test dependencies:
```bash
pip install -r requirements-dev.txt
```

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Release tags

## Coverage Goals

- Unit tests: >80% coverage
- Integration tests: Critical paths covered
- API tests: All endpoints tested
