from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from src.course.domain.chapter_body import ChapterBody
from src.course.domain.exceptions import AlreadyArchivedError, NotArchivedError
from src.course.domain.title import Title


@dataclass
class Chapter:
    id: UUID
    title: Title
    body: ChapterBody
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    archived_at: Optional[datetime] = None

    def update_title(self, title: Title) -> None:
        self.title = title
        self.updated_at = datetime.now(timezone.utc)

    def update_body(self, body: ChapterBody) -> None:
        self.body = body
        self.updated_at = datetime.now(timezone.utc)

    def archive(self):
        if self.is_archived:
            raise AlreadyArchivedError()

        now = datetime.now(timezone.utc)
        self.archived_at = now
        self.updated_at = now

    def unarchive(self):
        if not self.is_archived:
            raise NotArchivedError()

        self.archived_at = None
        self.updated_at = datetime.now(timezone.utc)

    @property
    def is_archived(self) -> bool:
        return self.archived_at is not None
