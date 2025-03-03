from enum import Enum
from typing import Type, Union

from ..models.project import Project
from ..models.inverse import Inverse


class EventName(str, Enum):
    """Enumeration of possible event types for globalMOO models."""
    PROJECT_CREATED = "project.created"
    INVERSE_SUGGESTED = "inverse.suggested"

    def data_type(self) -> Type[Union[Project, Inverse]]:
        """Get the expected data type for this event."""
        data_type = {
            self.PROJECT_CREATED: Project,
            self.INVERSE_SUGGESTED: Inverse
        }[self]

        return data_type