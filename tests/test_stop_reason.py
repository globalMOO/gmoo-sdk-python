"""Tests for stop reason handling."""
import pytest
from globalmoo.enums.stop_reason import StopReason

class TestStopReason:
    """Tests for StopReason enum."""

    @pytest.mark.parametrize("reason,expected", [
        (StopReason.RUNNING, False),
        (StopReason.SATISFIED, True),
        (StopReason.STOPPED, True),
        (StopReason.EXHAUSTED, True),
    ])
    def test_should_stop(self, reason: StopReason, expected: bool):
        """Should correctly indicate if optimization should stop."""
        assert reason.should_stop() == expected

    def test_is_running(self):
        """Should correctly identify running state."""
        assert StopReason.RUNNING.is_running() is True
        assert StopReason.SATISFIED.is_running() is False
        assert StopReason.STOPPED.is_running() is False
        assert StopReason.EXHAUSTED.is_running() is False

    def test_is_satisfied(self):
        """Should correctly identify satisfied state."""
        assert StopReason.RUNNING.is_satisfied() is False
        assert StopReason.SATISFIED.is_satisfied() is True
        assert StopReason.STOPPED.is_satisfied() is False
        assert StopReason.EXHAUSTED.is_satisfied() is False

    def test_is_stopped(self):
        """Should correctly identify stopped state."""
        assert StopReason.RUNNING.is_stopped() is False
        assert StopReason.SATISFIED.is_stopped() is False
        assert StopReason.STOPPED.is_stopped() is True
        assert StopReason.EXHAUSTED.is_stopped() is False

    def test_is_exhausted(self):
        """Should correctly identify exhausted state."""
        assert StopReason.RUNNING.is_exhausted() is False
        assert StopReason.SATISFIED.is_exhausted() is False
        assert StopReason.STOPPED.is_exhausted() is False
        assert StopReason.EXHAUSTED.is_exhausted() is True