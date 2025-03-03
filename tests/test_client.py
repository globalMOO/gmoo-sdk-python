class TestClientEventHandling:
    """Tests for event handling."""

    def test_handle_event_valid_project_created(self, client):
        """Should successfully handle a project.created event."""
        payload = json.dumps({
            "id": 1,
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-01T00:00:00Z",
            "disabledAt": None,
            "name": "project.created",
            "subject": "test-subject",
            "data": {
                "id": 1,
                "createdAt": "2025-01-01T00:00:00Z",
                "updatedAt": "2025-01-01T00:00:00Z",
                "disabledAt": None,
                "developedAt": None,
                "name": "Test Project",
                "inputCount": 2,
                "minimums": [0.0, 0.0],
                "maximums": [1.0, 1.0],
                "inputTypes": ["float", "float"],
                "categories": [],
                "inputCases": [[0.5, 0.5]],
                "caseCount": 1
            }
        })

        event = client.handle_event(payload)
        assert event.name == EventName.PROJECT_CREATED
        assert isinstance(event.data, Project)

    def test_handle_event_valid_inverse_suggested(self, client):
        """Should successfully handle an inverse.suggested event."""
        payload = json.dumps({
            "id": 1,
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-01T00:00:00Z",
            "disabledAt": None,
            "name": "inverse.suggested",
            "subject": "test-subject",
            "data": {
                "id": 1,
                "createdAt": "2025-01-01T00:00:00Z",
                "updatedAt": "2025-01-01T00:00:00Z",
                "disabledAt": None,
                "loadedAt": None,
                "satisfiedAt": None,
                "stoppedAt": None,
                "exhaustedAt": None,
                "iteration": 1,
                "input": [0.5, 1.0],
                "suggestTime": 0,
                "computeTime": 0
            }
        })

        event = client.handle_event(payload)
        assert event.name == EventName.INVERSE_SUGGESTED
        assert isinstance(event.data, Inverse)

    def test_handle_event_invalid_json(self, client):
        """Should raise on invalid JSON payload."""
        with pytest.raises(InvalidArgumentException) as exc:
            client.handle_event("invalid json")
        assert "not valid JSON" in str(exc.value)

    def test_handle_event_missing_required_fields(self, client):
        """Should raise when required fields are missing."""
        with pytest.raises(InvalidArgumentException) as exc:
            client.handle_event('{"foo": "bar"}')
        assert "not appear to be a valid event" in str(exc.value)

    def test_handle_event_invalid_name(self, client):
        """Should raise on invalid event name."""
        payload = json.dumps({
            "id": 1,
            "name": "invalid.event",
            "data": {}
        })
        with pytest.raises(InvalidArgumentException) as exc:
            client.handle_event(payload)
        assert "invalid" in str(exc.value)
# tests/test_client.py
from datetime import datetime
import pytest
from unittest.mock import Mock, call
import httpx
import json

from globalmoo.client import Client
from globalmoo.credentials import Credentials
from globalmoo.exceptions.invalid_argument import InvalidArgumentException
from globalmoo.exceptions.network_connection import NetworkConnectionException
from globalmoo.exceptions.invalid_request import InvalidRequestException
from globalmoo.exceptions.invalid_response import InvalidResponseException
from globalmoo.enums.input_type import InputType
from globalmoo.enums.objective_type import ObjectiveType
from globalmoo.enums.event_name import EventName
from globalmoo.models.project import Project
from globalmoo.models.inverse import Inverse
from globalmoo.request.create_model import CreateModel
from globalmoo.request.create_project import CreateProject
from globalmoo.request.load_output_cases import LoadOutputCases
from globalmoo.request.load_objectives import LoadObjectives
from globalmoo.request.suggest_inverse import SuggestInverse
from globalmoo.request.load_inversed_output import LoadInversedOutput
from globalmoo.request.register_account import RegisterAccount
from globalmoo.request.read_models import ReadModels
from globalmoo.request.read_trial import ReadTrial


class TestClientObjectiveOperations:
    """Tests for objective-related operations."""

    def test_load_objectives_success(self, client, mock_http_client, sample_objective_data):
        """Should successfully load objectives."""
        # Setup
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = sample_objective_data
        mock_response.raise_for_status.return_value = None
        mock_http_client.request.return_value = mock_response

        # Execute
        request = LoadObjectives(
        trial_id=1,
        objectives=[1.0, 2.0],
        objective_types=[ObjectiveType.MINIMIZE, ObjectiveType.MAXIMIZE],
        initial_input=[0.5, 1.0],
        initial_output=[1.0, 2.0],
        minimum_bounds=[0.9, 1.8],
        maximum_bounds=[1.1, 2.2]
        )
        objective = client.execute_request(request)

        # Verify
        assert objective.id == sample_objective_data["id"]
        assert objective.desired_l1_norm == sample_objective_data['desired_l1_norm']
        assert len(objective.inverses) == 0
        assert objective.last_inverse is None
        mock_http_client.request.assert_called_once_with(
            method="POST",
            url="/trials/1/objectives",
            json={
                "desiredL1Norm": 0.0,  # Default value now
                "objectives": [1.0, 2.0],
                "objectiveTypes": ["minimize", "maximize"],  # Lower case values
                "minimumBounds": [0.9, 1.8],  # Using provided bounds
                "maximumBounds": [1.1, 2.2],  # Using provided bounds
                "initialInput": [0.5, 1.0],
                "initialOutput": [1.0, 2.0]
            }
        )

    def test_suggest_inverse_success(self, client, mock_http_client, sample_inverse_data):
        """Should successfully suggest next inverse step."""
        # Add required fields to sample data
        sample_data = sample_inverse_data.copy()
        sample_data["l1_norm"] = 0.0
        sample_data["suggest_time"] = 0
        sample_data["compute_time"] = 0

        # Setup
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = sample_data
        mock_response.raise_for_status.return_value = None
        mock_http_client.request.return_value = mock_response

        # Execute
        request = SuggestInverse(
        objective_id=1
        )
        inverse = client.execute_request(request)

        # Verify
        assert inverse.id == sample_data["id"]
        assert inverse.iteration == 1
        assert inverse.output is None
        assert not inverse.should_stop()
        mock_http_client.request.assert_called_once_with(
            method="POST",
            url="/objectives/1/suggest-inverse",
            json={}
        )

    def test_load_inverse_output_success(self, client, mock_http_client, sample_inverse_data):
        """Should successfully load inverse output."""
        # Update sample data for output loading
        sample_data = sample_inverse_data.copy()
        sample_data["loaded_at"] = "2025-01-01T00:00:00Z"
        sample_data["output"] = [3.0, 4.0]
        sample_data["l1_norm"] = 0.0
        sample_data["suggest_time"] = 0
        sample_data["compute_time"] = 0
        
        # Setup
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = sample_data
        mock_response.raise_for_status.return_value = None
        mock_http_client.request.return_value = mock_response

        # Execute
        request = LoadInversedOutput(
        inverse_id=1,
        output=[3.0, 4.0]
        )
        inverse = client.execute_request(request)

        # Verify
        assert inverse.id == sample_data["id"]
        assert inverse.output == [3.0, 4.0]
        assert inverse.loaded_at is not None
        mock_http_client.request.assert_called_once_with(
            method="POST",
            url="/inverses/1/load-output",
            json={
                "output": [3.0, 4.0]
            }
        )