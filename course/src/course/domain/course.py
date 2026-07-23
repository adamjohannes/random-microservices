from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4
from chapter import Chapter
from src.course.domain.title import Title
from src.course.domain.exceptions import AlreadyArchivedError, NotArchivedError
from src.course.domain.user import User


@dataclass
class Course:
    id: UUID
    author: User
    title: Title
    description: str
    chapters: List[Chapter] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    archived_at: Optional[datetime] = None

    def add_chapter(self, title: str, body: str) -> Chapter:
        chapter = Chapter(id=uuid4(), title=title, body=body)
        self.chapters.append(chapter)
        self.updated_at = datetime.now(timezone.utc)
        return chapter

    def archive(self):
        if self.archived_at is None:
            now = datetime.now(timezone.utc)
            self.archived_at = now
            self.updated_at = now
        raise AlreadyArchivedError()

    def unarchive(self):
        if self.archived_at is not None:
            self.archived_at = None
            self.updated_at = datetime.now(timezone.utc)
        raise NotArchivedError()

    @property
    def is_archived(self) -> bool:
        return self.archived_ad is not None
