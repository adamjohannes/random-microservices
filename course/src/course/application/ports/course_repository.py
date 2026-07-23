from typing import Optional, Protocol
from uuid import UUID

from src.course.domain.course import Course

class CourseRepository(Protocol):
    """
    Port for Course data access.
    Treats the Course Aggregate Root as a slight unit of work.
    """

    async def save(self, course: Course) -> None:
        """
        Saves a course and all its child entities (chapters, assignees).
        This handles both creation and updates (upsert).
        """
        ...

    async def get_by_id(self, user_id: UUID) -> Optional[Course]:
        """Fetches a full course aggregate by its ID."""
        ...
