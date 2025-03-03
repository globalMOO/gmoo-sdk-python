# tests/conftest.py
from datetime import datetime
import pytest
from unittest.mock import Mock
import httpx

from globalmoo.credentials import Credentials
from globalmoo.client import Client
from globalmoo.enums.stop_reason import StopReason
from globalmoo.enums.input_type import InputType
from globalmoo.enums.objective_type import ObjectiveType
from globalmoo.enums.stop_reason import StopReason

@pytest.fixture
def mock_credentials():
    return Credentials(api_key="test-key", base_uri="https://test.api")

@pytest.fixture
def mock_http_client():
    return Mock(spec=httpx.Client)

@pytest.fixture
def client(mock_credentials, mock_http_client):
    return Client(credentials=mock_credentials, http_client=mock_http_client)

@pytest.fixture
def sample_model_data():
    return {
        "id": 1,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "disabled_at": None,
        "name": "Test Model",
        "description": None,
        "projects": []
    }

@pytest.fixture
def sample_project_data():
    return {
        "id": 1,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "disabled_at": None,
        "developed_at": None,
        "input_count": 2,
        "minimums": [0.0, 0.0],
        "maximums": [1.0, 1.0],
        "input_types": ["float", "category"],
        "categories": ["A", "B", "C"],
        "input_cases": [[0.5, 0.0], [0.5, 1.0], [0.5, 2.0]],
        "case_count": 3,
        "trials": []
    }

@pytest.fixture
def sample_trial_data():
    return {
        "id": 1,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "disabled_at": None,
        "output_count": 2,
        "output_cases": [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]],
        "objectives": []
    }

@pytest.fixture
def sample_objective_data():
    return {
        "id": 1,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "disabled_at": None,
        "attempts": 0,
        "stop_reason": StopReason.RUNNING,
        "desired_l1_norm": 0.1,
        "objectives": [1.0, 2.0],
        "objective_types": [ObjectiveType.MINIMIZE.value, ObjectiveType.MAXIMIZE.value],
        "minimumBounds": [0.9, 1.8],
        "maximumBounds": [1.1, 2.2],
        "inverses": [],
        "last_inverse": None
    }

@pytest.fixture
def sample_inverse_data():
    return {
        "id": 1,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "disabled_at": None,
        "loaded_at": None,
        "satisfied_at": None,
        "stopped_at": None,
        "exhausted_at": None,
        "iteration": 1,
        "l1_norm": 0.0,
        "suggest_time": 0,
        "compute_time": 0,
        "input": [0.5, 1.0],
        "output": None,
        "results": []
    }

@pytest.fixture
def sample_account_data():
    return {
        "id": 1,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "disabled_at": None,
        "company": "Test Company",
        "name": "Test User",
        "email": "test@example.com",
        "api_key": "test-key",
        "time_zone": "UTC",
        "customer_id": "cus_123456789"
    }
