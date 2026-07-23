from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from src.course.domain.user_email import UserEmail
from src.course.domain.user_name import UserName


@dataclass
class User:
    """
    A user known to the Course service, mirrored from the Account service.

    Attributes:
        id: user id (same as the originating account id)
        name: user name
        email: user email
        created_at: user creation date
        updated_at: user update date
    """
    id: UUID
    name: UserName
    email: UserEmail
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, account_id: UUID, name_str: str, email_str: str) -> "User":
        """
        Factory for registering a known user from the Account service
        into the Course service domain.

        Args:
            account_id: The originating account id, reused as the user id.
            name_str: Raw name text, validated into a UserName.
            email_str: Raw email text, validated into a UserEmail.

        Raises:
            InvalidNameLenghtError: If name_str is not 2-50 characters.
            InvalidNameCharacterError: If name_str contains non-alphabetical characters.
            EmptyEmailError: If email_str is empty.
            InvalidEmailFormatError: If email_str is not a valid email.
        """
        now = datetime.now(timezone.utc)
        return cls(
            id=account_id,
            name=UserName(name_str),
            email=UserEmail(email_str),
            created_at=now,
            updated_at=now
        )

    def update_name(self, name: UserName) -> None:
        """Replace the user's name."""
        self.name = name
        self.updated_at = datetime.now(timezone.utc)

    def update_email(self, email: UserEmail) -> None:
        """Replace the user's email."""
        self.email = email
        self.updated_at = datetime.now(timezone.utc)
