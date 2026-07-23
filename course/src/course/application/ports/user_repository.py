from typing import Optional, Protocol
from uuid import UUID

from src.course.domain.user import User

class UserRepository(Protocol):
    """
    Port for User data access.
    """

    async def save(self, user: User) -> None:
        """Saves a new user or updates an existing one."""
        ...

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Fetches a user by their ID, returning None if not found."""
        ...
