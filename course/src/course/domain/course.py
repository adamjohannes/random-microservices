from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Set
from uuid import UUID, uuid4

from course_chapter import CourseChapter
from src.course.domain.chapter_body import ChapterBody
from src.course.domain.title import Title
from src.course.domain.exceptions import AlreadyArchivedError, NotArchivedError, DomainValidationError
from src.course.domain.user import User


@dataclass
class Course:
    id: UUID
    author: User
    title: Title
    description: str
    chapters: List[CourseChapter] = field(default_factory=list)
    assignee_ids: Set[UUID] = field(default_factory=set)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    archived_at: Optional[datetime] = None

    @classmethod
    def create(cls, author: User, title_str: str, description: str) -> "Course":
        """
        Factory for creating a brand new Course.
        Instantiates Value Objects and generates default metadata.
        """
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            author=author,
            title=Title(title_str),
            description=description,
            chapters=[],
            created_at=now,
            updated_at=now,
            archived_at=None
        )

    def add_chapter(self, title: str, body: str) -> CourseChapter:
        chapter = CourseChapter(id=uuid4(), title=Title(title), body=ChapterBody(body))
        self.chapters.append(chapter)
        self.updated_at = datetime.now(timezone.utc)
        return chapter

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

    def enroll_user(self, user_id: UUID) -> None:
        if user_id == self.author.id:
            raise DomainValidationError("author cannot be assigned to their own course")

        self.assignee_ids.add(user_id)
        self.updated_at = datetime.now(timezone.utc)

    def unenroll_user(self, user_id: UUID) -> None:
        self.assignee_ids.discard(user_id)
        self.updated_at = datetime.now(timezone.utc)

    def update_chapter(self, chapter_id: UUID, title_str: str, body_str: str) -> None:
        chapter = next((c for c in self.chapters if c.id == chapter_id), None)
        if not chapter:
            raise DomainValidationError(f"chapter {chapter_id} not found in this course")

        chapter.update_title(Title(title_str))
        chapter.update_body(ChapterBody(body_str))

        self.updated_at = datetime.now(timezone.utc)
