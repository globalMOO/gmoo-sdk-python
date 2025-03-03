# globalmoo/enums/stop_reason.py
from enum import IntEnum
from typing import Literal


class StopReason(IntEnum):
    """Enumeration of possible reasons for a trial to stop."""
    RUNNING = 0
    SATISFIED = 1
    STOPPED = 2
    EXHAUSTED = 3

    def description(self) -> str:
        """Get a human-readable description of the stop reason."""
        descriptions = {
            self.RUNNING: "is still running or being evaluated",
            self.SATISFIED: "satisfied to an optimal input and output",
            self.STOPPED: "stopped due to duplicate suggested inputs",
            self.EXHAUSTED: "exhausted all attempts to converge"
        }
        return descriptions[self]

    def is_running(self) -> bool:
        """Check if the optimization is still running."""
        return self == self.RUNNING

    def is_satisfied(self) -> bool:
        """Check if the optimization is satisfied."""
        return self == self.SATISFIED

    def is_stopped(self) -> bool:
        """Check if the optimization was stopped."""
        return self == self.STOPPED

    def is_exhausted(self) -> bool:
        """Check if the optimization was exhausted."""
        return self == self.EXHAUSTED

    def should_stop(self) -> bool:
        """Determine if this stop reason indicates the trial should stop."""
        return self != self.RUNNING