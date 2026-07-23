from typing import Optional, Protocol, List
from uuid import UUID

from src.course.domain.course import Course


class CourseRepository(Protocol):
    """
    Port for Course data access.
    Treats the Course Aggregate Root as a single unit of work.
    """

    async def save(self, course: Course) -> None:
        """
        Saves a course and all its child entities (chapters, assignees).
        This handles both creation and updates (upsert).
        """
        ...

    async def get_by_id(self, course_id: UUID) -> Optional[Course]:
        """Fetches a full course aggregate by its ID."""
        ...

    async def get_all(self, limit: int = 10, offset: int = 0) -> List[Course]:
        """Fetches a paginated list of all courses."""
        ...

    async def get_by_author_id(self, author_id: UUID) -> List[Course]:
        """Fetches all courses authored by a specific user."""
        ...

    async def get_by_assignee_id(self, assignee_id: UUID) -> List[Course]:
        """Fetches all courses assigned to a specific user."""
        ...
