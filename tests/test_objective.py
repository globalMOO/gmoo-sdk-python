"""Tests for objective satisfaction checking."""
from datetime import datetime

import pytest

from globalmoo.enums.objective_type import ObjectiveType
from globalmoo.enums.stop_reason import StopReason
from globalmoo.models.objective import Objective
from globalmoo.models.inverse import Inverse


class TestObjective:
    """Tests for Objective model."""

    def test_iteration_count(self):
        """Should return correct number of iterations."""
        objective = self.create_objective(8)
        assert objective.iteration_count == 8

    def test_last_inverse_with_no_inverses(self):
        """Should return None when no inverses exist."""
        objective = self.create_objective(0)
        assert objective.last_inverse is None

    def test_last_inverse_with_inverses(self):
        """Should return the last inverse when inverses exist."""
        objective = self.create_objective(3)
        assert objective.last_inverse == objective.inverses[-1]

    def create_objective(self, inverse_count: int = 0) -> Objective:
        """Helper to create an objective for testing."""
        stop_reason = StopReason.SATISFIED
        created_at = datetime.now()

        inverses = []
        for i in range(inverse_count):
            inverse = Inverse(
                id=i + 1,
                created_at=created_at,
                updated_at=created_at,
                disabled_at=None,
                loadedAt=None,
                satisfiedAt=None,
                stoppedAt=None,
                exhaustedAt=None,
                iteration=i + 1,
                input=[1.0, 2.0],
                output=None,
                errors=None,
                suggest_time=0,
                compute_time=0
            )
            inverses.append(inverse)

        objective = Objective(
            id=1,
            created_at=created_at,
            updated_at=created_at,
            disabled_at=None,
            optimal_inverse=None,
            attempt_count=0,
            stop_reason=stop_reason,
            desired_l1_norm=0.0,
            objectives=[1.0],
            objective_types=[ObjectiveType.EXACT],
            minimum_bounds=[0.0],
            maximum_bounds=[0.0],
            inverses=inverses
        )

        return objective