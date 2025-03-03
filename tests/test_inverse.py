# tests/test_inverse.py
from datetime import datetime
from globalmoo.models.inverse import Inverse
from globalmoo.enums.stop_reason import StopReason


class TestInverse:
    """Tests for Inverse model."""

    def test_get_stop_reason_running(self):
        """Should return RUNNING when no stop dates are set."""
        inverse = Inverse(
            id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            disabled_at=None,
            loaded_at=None,
            satisfied_at=None,
            stopped_at=None,
            exhausted_at=None,
            iteration=1,
            l1_norm=0.0,
            suggest_time=0,
            compute_time=0,
            input=[1.0, 2.0],
            output=None,
            results=[]
        )
        assert inverse.get_stop_reason() == StopReason.RUNNING
        assert not inverse.should_stop()

    def test_get_stop_reason_satisfied(self):
        """Should return SATISFIED when satisfied_at is set."""
        inverse = Inverse(
            id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            disabled_at=None,
            loaded_at=datetime.now(),
            satisfied_at=datetime.now(),
            stopped_at=None,
            exhausted_at=None,
            iteration=1,
            l1_norm=0.1,
            suggest_time=0,
            compute_time=0,
            input=[1.0, 2.0],
            output=[3.0, 4.0],
            results=[
                {
                    "id": 1,
                    "createdAt": datetime.now(),
                    "updatedAt": datetime.now(),
                    "number": 0,
                    "type": "exact",
                    "objective": 1.0,
                    "output": 3.0,
                    "minimumBound": 0.0,
                    "maximumBound": 0.0,
                    "error": 0.1,
                    "detail": "L1 norm is less than desired L1 norm across all exact objectives",
                    "satisfied": True
                },
                {
                    "id": 2,
                    "createdAt": datetime.now(),
                    "updatedAt": datetime.now(),
                    "number": 1,
                    "type": "exact",
                    "objective": 2.0,
                    "output": 4.0,
                    "minimumBound": 0.0,
                    "maximumBound": 0.0,
                    "error": 0.1,
                    "detail": "L1 norm is less than desired L1 norm across all exact objectives",
                    "satisfied": True
                }
            ]
        )
        assert inverse.get_stop_reason() == StopReason.SATISFIED
        assert inverse.should_stop()

    def test_get_stop_reason_stopped(self):
        """Should return STOPPED when stopped_at is set."""
        inverse = Inverse(
            id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            disabled_at=None,
            loaded_at=datetime.now(),
            satisfied_at=None,
            stopped_at=datetime.now(),
            exhausted_at=None,
            iteration=1,
            l1_norm=0.1,
            suggest_time=0,
            compute_time=0,
            input=[1.0, 2.0],
            output=[3.0, 4.0],
            results=[
                {
                    "id": 1,
                    "createdAt": datetime.now(),
                    "updatedAt": datetime.now(),
                    "number": 0,
                    "type": "exact",
                    "objective": 1.0,
                    "output": 3.0,
                    "minimumBound": 0.0,
                    "maximumBound": 0.0,
                    "error": 0.2,
                    "detail": "L1 norm is greater than or equal to desired L1 norm",
                    "satisfied": False
                },
                {
                    "id": 2,
                    "createdAt": datetime.now(),
                    "updatedAt": datetime.now(),
                    "number": 1,
                    "type": "exact",
                    "objective": 2.0,
                    "output": 4.0,
                    "minimumBound": 0.0,
                    "maximumBound": 0.0,
                    "error": 0.2,
                    "detail": "L1 norm is greater than or equal to desired L1 norm",
                    "satisfied": False
                }
            ]
        )
        assert inverse.get_stop_reason() == StopReason.STOPPED
        assert inverse.should_stop()

    def test_get_stop_reason_exhausted(self):
        """Should return EXHAUSTED when exhausted_at is set."""
        inverse = Inverse(
            id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            disabled_at=None,
            loaded_at=datetime.now(),
            satisfied_at=None,
            stopped_at=None,
            exhausted_at=datetime.now(),
            iteration=1,
            l1_norm=0.1,
            suggest_time=0,
            compute_time=0,
            input=[1.0, 2.0],
            output=[3.0, 4.0],
            results=[
                {
                    "id": 1,
                    "createdAt": datetime.now(),
                    "updatedAt": datetime.now(),
                    "number": 0,
                    "type": "exact",
                    "objective": 1.0,
                    "output": 3.0,
                    "minimumBound": 0.0,
                    "maximumBound": 0.0,
                    "error": 0.3,
                    "detail": "L1 norm is greater than or equal to desired L1 norm",
                    "satisfied": False
                },
                {
                    "id": 2,
                    "createdAt": datetime.now(),
                    "updatedAt": datetime.now(),
                    "number": 1,
                    "type": "exact",
                    "objective": 2.0,
                    "output": 4.0,
                    "minimumBound": 0.0,
                    "maximumBound": 0.0,
                    "error": 0.3,
                    "detail": "L1 norm is greater than or equal to desired L1 norm",
                    "satisfied": False
                }
            ]
        )
        assert inverse.get_stop_reason() == StopReason.EXHAUSTED
        assert inverse.should_stop()

    def test_multiple_stop_dates(self):
        """Should prioritize satisfied over other stop reasons when multiple dates are set."""
        now = datetime.now()
        inverse = Inverse(
            id=1,
            created_at=now,
            updated_at=now,
            disabled_at=None,
            loaded_at=now,
            satisfied_at=now,
            stopped_at=now,
            exhausted_at=now,
            iteration=1,
            l1_norm=0.1,
            suggest_time=0,
            compute_time=0,
            input=[1.0, 2.0],
            output=[3.0, 4.0],
            results=[
                {
                    "id": 1,
                    "createdAt": now,
                    "updatedAt": now,
                    "number": 0,
                    "type": "exact",
                    "objective": 1.0,
                    "output": 3.0,
                    "minimumBound": 0.0,
                    "maximumBound": 0.0,
                    "error": 0.1,
                    "detail": "L1 norm is less than desired L1 norm across all exact objectives",
                    "satisfied": True
                },
                {
                    "id": 2,
                    "createdAt": now,
                    "updatedAt": now,
                    "number": 1,
                    "type": "exact",
                    "objective": 2.0,
                    "output": 4.0,
                    "minimumBound": 0.0,
                    "maximumBound": 0.0,
                    "error": 0.1,
                    "detail": "L1 norm is less than desired L1 norm across all exact objectives",
                    "satisfied": True
                }
            ]
        )
        assert inverse.get_stop_reason() == StopReason.SATISFIED
        assert inverse.should_stop()

    def test_partial_output_state(self):
        """Should handle state when output is loaded but not yet evaluated."""
        inverse = Inverse(
            id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            disabled_at=None,
            loaded_at=datetime.now(),
            satisfied_at=None,
            stopped_at=None,
            exhausted_at=None,
            iteration=1,
            l1_norm=0.0,
            suggest_time=0,
            compute_time=0,
            input=[1.0, 2.0],
            output=[3.0, 4.0],
            results=[]
        )
        assert inverse.get_stop_reason() == StopReason.RUNNING
        assert not inverse.should_stop()

    def test_get_objective_errors(self):
        """Should return error values for each objective."""
        now = datetime.now()
        inverse = Inverse(
            id=1,
            created_at=now,
            updated_at=now,
            disabled_at=None,
            loaded_at=None,
            satisfied_at=None,
            stopped_at=None,
            exhausted_at=None,
            iteration=1,
            l1_norm=0.1,
            suggest_time=0,
            compute_time=0,
            input=[1.0, 2.0],
            output=[3.0, 4.0],
            results=[
                {
                    "id": 1,
                    "createdAt": now,
                    "updatedAt": now,
                    "number": 0,
                    "type": "exact",
                    "objective": 1.0,
                    "output": 3.0,
                    "minimumBound": 0.0,
                    "maximumBound": 0.0,
                    "error": 0.1,
                    "detail": "test detail",
                    "satisfied": True
                },
                {
                    "id": 2,
                    "createdAt": now,
                    "updatedAt": now,
                    "number": 1,
                    "type": "exact",
                    "objective": 2.0,
                    "output": 4.0,
                    "minimumBound": 0.0,
                    "maximumBound": 0.0,
                    "error": 0.2,
                    "detail": "test detail",
                    "satisfied": True
                }
            ]
        )
        assert inverse.get_objective_errors() == [0.1, 0.2]

    def test_get_objective_errors_no_results(self):
        """Should return empty list when no results exist."""
        inverse = Inverse(
            id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            disabled_at=None,
            loaded_at=None,
            satisfied_at=None,
            stopped_at=None,
            exhausted_at=None,
            iteration=1,
            l1_norm=0.0,
            suggest_time=0,
            compute_time=0,
            input=[1.0, 2.0],
            output=None,
            results=None
        )
        assert inverse.get_objective_errors() == []