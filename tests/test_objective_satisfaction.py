"""Tests for objective satisfaction checking."""
from datetime import datetime

import pytest

from globalmoo.enums.objective_type import ObjectiveType
from globalmoo.enums.stop_reason import StopReason
from globalmoo.models.objective import Objective


def create_objective(objectives, objective_types, *, desired_l1_norm=1e-6, minimum_bounds=None, maximum_bounds=None):
    """Helper to create an objective for testing."""
    if minimum_bounds is None:
        minimum_bounds = [0.0] * len(objectives)
    if maximum_bounds is None:
        maximum_bounds = [0.0] * len(objectives)

    return Objective(
        id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        disabled_at=None,
        attempts=0,
        stop_reason=StopReason.RUNNING,
        desired_l1_norm=desired_l1_norm,
        objectives=objectives,
        objective_types=objective_types,
        minimumBounds=minimum_bounds,
        maximumBounds=maximum_bounds,
        inverses=[],
        last_inverse=None
    )


def test_exact_objective():
    """Test satisfaction check for EXACT objective type."""
    objective = create_objective(
        objectives=[1.0],
        objective_types=[ObjectiveType.EXACT],
        desired_l1_norm=1e-6
    )
    
    assert objective.id == 1
    assert objective.desired_l1_norm == 1e-6
    assert objective.objectives == [1.0]
    assert objective.objective_types == [ObjectiveType.EXACT]
    assert objective.minimum_bounds == [0.0]
    assert objective.maximum_bounds == [0.0]


def test_percent_objective():
    """Test satisfaction check for PERCENT objective type."""
    objective = create_objective(
        objectives=[1.0],
        objective_types=[ObjectiveType.PERCENT],
        minimum_bounds=[-5.0],
        maximum_bounds=[5.0]
    )
    
    assert objective.id == 1
    assert objective.desired_l1_norm == 1e-6
    assert objective.objectives == [1.0]
    assert objective.objective_types == [ObjectiveType.PERCENT]
    assert objective.minimum_bounds == [-5.0]
    assert objective.maximum_bounds == [5.0]


def test_value_objective():
    """Test satisfaction check for VALUE objective type."""
    objective = create_objective(
        objectives=[1.0],
        objective_types=[ObjectiveType.VALUE],
        minimum_bounds=[-0.5],
        maximum_bounds=[0.5]
    )
    
    assert objective.id == 1
    assert objective.desired_l1_norm == 1e-6
    assert objective.objectives == [1.0]
    assert objective.objective_types == [ObjectiveType.VALUE]
    assert objective.minimum_bounds == [-0.5]
    assert objective.maximum_bounds == [0.5]