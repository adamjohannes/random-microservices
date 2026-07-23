from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Set
from uuid import UUID, uuid4

from src.course.domain.course_chapter import CourseChapter
from src.course.domain.chapter_body import ChapterBody
from src.course.domain.course_description import CourseDescription
from src.course.domain.title import Title
from src.course.domain.exceptions import AlreadyArchivedError, NotArchivedError, NotCourseAuthorError, \
    AuthorCannotBeAssigneeError, ChapterNotFoundError, ArchivedCourseError
from src.course.domain.user import User


@dataclass
class Course:
    """
    A course is a collection of knowledge divided in chapters.

    Attributes:
        id: course id
        author: course author
        title: course title
        description: course description
        chapters: list of course chapters
        assignee_ids: set of users who have assigned to this course
        created_at: course creation date
        updated_at: course update date
        archived_at: course archive date
    """
    id: UUID
    author: User
    title: Title
    description: CourseDescription
    chapters: List[CourseChapter] = field(default_factory=list)
    assignee_ids: Set[UUID] = field(default_factory=set)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    archived_at: Optional[datetime] = None

    @classmethod
    def create(cls, author: User, title_str: str, description: str) -> "Course":
        """
        Factory for creating a brand new Course.

        Args:
            author: The user who owns and can modify the course.
            title_str: Raw title text, validated into a Title.
            description: Raw description text, validated into a CourseDescription.

        Raises:
            InvalidTitleLength: If title_str fails Title validation.
            InvalidCourseDescriptionLenght: If description fails CourseDescription validation.
        """
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            author=author,
            title=Title(title_str),
            description=CourseDescription(description),
            chapters=[],
            created_at=now,
            updated_at=now,
            archived_at=None
        )

    def add_chapter(self, title: str, body: str, actor_id: UUID) -> CourseChapter:
        """
        Append a new chapter to the course.

        Args:
            title: Raw chapter title, validated into a Title.
            body: Raw chapter content, validated into a ChapterBody.
            actor_id: The user performing the action; must be the author.

        Raises:
            ArchivedCourseError: If the course is archived.
            NotCourseAuthorError: If actor_id is not the course author.
            InvalidTitleLength: If title fails Title validation.
            InvalidChapterBodyLength: If body fails ChapterBody validation.
        """
        self._ensure_modifiable()
        self._ensure_author(actor_id)

        chapter = CourseChapter(id=uuid4(), index=len(self.chapters), title=Title(title), body=ChapterBody(body))
        self.chapters.append(chapter)
        self.updated_at = datetime.now(timezone.utc)
        return chapter

    def archive(self, actor_id: UUID) -> None:
        """
        Archive the course, making it read-only.

        Args:
            actor_id: The user performing the action; must be the author.

        Raises:
            NotCourseAuthorError: If actor_id is not the course author.
            AlreadyArchivedError: If the course is already archived.
        """
        self._ensure_author(actor_id)

        if self.is_archived:
            raise AlreadyArchivedError()

        now = datetime.now(timezone.utc)
        self.archived_at = now
        self.updated_at = now

    def unarchive(self, actor_id: UUID) -> None:
        """
        Restore an archived course to a modifiable state.

        Args:
            actor_id: The user performing the action; must be the author.

        Raises:
            NotCourseAuthorError: If actor_id is not the course author.
            NotArchivedError: If the course is not currently archived.
        """
        self._ensure_author(actor_id)

        if not self.is_archived:
            raise NotArchivedError()

        self.archived_at = None
        self.updated_at = datetime.now(timezone.utc)

    def enroll_user(self, user_id: UUID) -> None:
        """
        Enroll a user as an assignee of the course.

        Args:
            user_id: The user to enroll; cannot be the course author.

        Raises:
            ArchivedCourseError: If the course is archived.
            AuthorCannotBeAssigneeError: If user_id is the course author.
        """
        self._ensure_modifiable()

        if user_id == self.author.id:
            raise AuthorCannotBeAssigneeError("author cannot be assigned to their own course")

        self.assignee_ids.add(user_id)
        self.updated_at = datetime.now(timezone.utc)

    def unenroll_user(self, user_id: UUID) -> None:
        """
        Remove a user from the course's assignees; a no-op if not enrolled.

        Args:
            user_id: The user to unenroll.

        Raises:
            ArchivedCourseError: If the course is archived.
        """
        self._ensure_modifiable()

        self.assignee_ids.discard(user_id)
        self.updated_at = datetime.now(timezone.utc)

    def update_chapter(self, actor_id: UUID, chapter_id: UUID, title_str: str, body_str: str) -> None:
        """
        Replace the title and body of an existing chapter.

        Args:
            actor_id: The user performing the action; must be the author.
            chapter_id: The id of the chapter to update.
            title_str: Raw chapter title, validated into a Title.
            body_str: Raw chapter content, validated into a ChapterBody.

        Raises:
            NotCourseAuthorError: If actor_id is not the course author.
            ArchivedCourseError: If the course is archived.
            ResourceStateError: If the chapter is archived.
            ChapterNotFoundError: If no chapter with chapter_id exists.
            InvalidTitleLength: If title_str fails Title validation.
            InvalidChapterBodyLength: If body_str fails ChapterBody validation.
        """
        self._ensure_author(actor_id)
        self._ensure_modifiable()

        chapter = next((c for c in self.chapters if c.id == chapter_id), None)
        if not chapter:
            raise ChapterNotFoundError(str(chapter_id))

        chapter.update_title(Title(title_str))
        chapter.update_body(ChapterBody(body_str))

        self.updated_at = datetime.now(timezone.utc)

    def archive_chapter(self, actor_id: UUID, chapter_id: UUID) -> None:
        """
        Archive a single chapter within the course.

        Args:
            actor_id: The user performing the action; must be the author.
            chapter_id: The id of the chapter to archive.

        Raises:
            NotCourseAuthorError: If actor_id is not the course author.
            ArchivedCourseError: If the course is archived.
            ChapterNotFoundError: If no chapter with chapter_id exists.
            AlreadyArchivedError: If the target chapter is already archived.
        """
        self._ensure_author(actor_id)
        self._ensure_modifiable()

        chapter = next((c for c in self.chapters if c.id == chapter_id), None)

        if not chapter:
            raise ChapterNotFoundError(str(chapter_id))

        chapter.archive()
        self.updated_at = datetime.now(timezone.utc)

    @property
    def is_archived(self) -> bool:
        return self.archived_at is not None

    def _ensure_modifiable(self) -> None:
        if self.is_archived:
            raise ArchivedCourseError()

    def _ensure_author(self, actor_id: UUID) -> None:
        if self.author.id != actor_id:
            raise NotCourseAuthorError()
