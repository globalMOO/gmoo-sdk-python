"""Tests for LoadObjectives request."""
import pytest
from globalmoo.request.load_objectives import LoadObjectives
from globalmoo.enums.objective_type import ObjectiveType


def test_load_objectives_initialization():
    """Test basic initialization of LoadObjectives request."""
    request = LoadObjectives(
        trial_id=1,
        objectives=[1.0, 2.0],
        objective_types=[ObjectiveType.EXACT, ObjectiveType.EXACT],
        initial_input=[0.5, 0.6],
        initial_output=[1.0, 2.0]
    )
    
    assert request.trial_id == 1
    assert request.objectives == [1.0, 2.0]
    assert request.initial_input == [0.5, 0.6]
    assert request.initial_output == [1.0, 2.0]
    assert request.desired_l1_norm == 0.0
    assert request.minimum_bounds == [0.0, 0.0]
    assert request.maximum_bounds == [0.0, 0.0]


def test_load_objectives_serialization():
    """Test that LoadObjectives serializes correctly for API request."""
    request = LoadObjectives(
        trial_id=1,
        objectives=[1.0, 2.0],
        objective_types=[ObjectiveType.EXACT, ObjectiveType.EXACT],
        initial_input=[0.5, 0.6],
        initial_output=[1.0, 2.0],
        desired_l1_norm=1e-6,
        minimum_bounds=[0.0, 0.0],
        maximum_bounds=[0.0, 0.0]
    )
    
    data = request.to_dict()
    assert data == {
        "desiredL1Norm": 1e-6,
        "objectives": [1.0, 2.0],
        "objectiveTypes": ["exact", "exact"],
        "initialInput": [0.5, 0.6],
        "initialOutput": [1.0, 2.0],
        "minimumBounds": [0.0, 0.0],
        "maximumBounds": [0.0, 0.0]
    }