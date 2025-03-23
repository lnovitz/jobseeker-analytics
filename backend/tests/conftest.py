import sys
import os
from fastapi.testclient import TestClient
import pytest

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client