from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from src.course.domain.user_email import UserEmail
from src.course.domain.user_name import UserName


@dataclass
class User:
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
        self.name = name
        self.updated_at = datetime.now(timezone.utc)

    def update_email(self, email: UserEmail) -> None:
        self.email = email
        self.updated_at = datetime.now(timezone.utc)
