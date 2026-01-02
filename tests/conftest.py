"""
Pytest configuration and shared fixtures
"""
import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="session")
def test_settings():
    """Test configuration settings"""
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["DEBUG"] = "False"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    return True