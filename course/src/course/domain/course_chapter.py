from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from src.course.domain.chapter_body import ChapterBody
from src.course.domain.exceptions import AlreadyArchivedError, NotArchivedError, ArchivedChapterError, \
    ArchivedChapterError
from src.course.domain.title import Title


@dataclass
class CourseChapter:
    """
    A course chapter represents an individual chapter of a course.

    Attributes:
        id: chapter id
        index: chapter index inside the course
        title: chapter title
        body: chapter content
        created_at: chapter creation time
        updated_at: chapter update time
        archived_at: chapter archive time
    """
    id: UUID
    index: int
    title: Title
    body: ChapterBody
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    archived_at: Optional[datetime] = None

    def update_title(self, title: Title) -> None:
        """
        Replace the chapter title.

        Args:
            title: The new validated title.

        Raises:
            ArchivedChapterError: If the chapter is archived.
        """
        self._ensure_modifiable()

        self.title = title
        self.updated_at = datetime.now(timezone.utc)

    def update_body(self, body: ChapterBody) -> None:
        """
        Replace the chapter body.

        Args:
            body: The new validated body content.

        Raises:
            ArchivedChapterError: If the chapter is archived.
        """
        self._ensure_modifiable()

        self.body = body
        self.updated_at = datetime.now(timezone.utc)

    def archive(self):
        """
        Archive the chapter, making it read-only.

        Raises:
            AlreadyArchivedError: If the chapter is already archived.
        """
        if self.is_archived:
            raise AlreadyArchivedError()

        now = datetime.now(timezone.utc)
        self.archived_at = now
        self.updated_at = now

    def unarchive(self):
        """
        Restore an archived chapter to a modifiable state.

        Raises:
            NotArchivedError: If the chapter is not currently archived.
        """
        if not self.is_archived:
            raise NotArchivedError()

        self.archived_at = None
        self.updated_at = datetime.now(timezone.utc)

    @property
    def is_archived(self) -> bool:
        return self.archived_at is not None

    def _ensure_modifiable(self) -> None:
        """Checks if the chapter has not been archived yet, and therefore is modifiable."""
        if self.is_archived:
            raise ArchivedChapterError()
