from uuid import uuid4

import pytest

from src.course.domain.exceptions import (
    AlreadyArchivedError,
    ArchivedCourseError,
    AuthorCannotBeAssigneeError,
    ChapterNotFoundError,
    InvalidTitleLength,
    NotArchivedError,
    NotCourseAuthorError,
)
from src.course.domain.course import Course
from src.course.domain.user import User


def make_user(name: str = "Adam Johannes", email: str = "adam@example.com") -> User:
    return User.create(account_id=uuid4(), name_str=name, email_str=email)


def make_course(author: User | None = None) -> Course:
    author = author or make_user()
    return Course.create(
        author=author,
        title_str="Introduction to Testing",
        description="A thorough introduction to software testing practices and tools.",
    )


class TestCourseCreate:
    def test_creates_with_valid_data(self) -> None:
        author = make_user()
        course = Course.create(author=author, title_str="Valid Title", description="A" * 30)
        assert str(course.title) == "Valid Title"
        assert course.author is author
        assert course.archived_at is None
        assert course.chapters == []

    def test_rejects_short_title(self) -> None:
        with pytest.raises(InvalidTitleLength):
            Course.create(author=make_user(), title_str="AB", description="A" * 30)


class TestCourseArchive:
    def test_author_can_archive(self) -> None:
        author = make_user()
        course = make_course(author)
        course.archive(actor_id=author.id)
        assert course.is_archived

    def test_non_author_cannot_archive(self) -> None:
        course = make_course()
        with pytest.raises(NotCourseAuthorError):
            course.archive(actor_id=uuid4())

    def test_cannot_archive_twice(self) -> None:
        author = make_user()
        course = make_course(author)
        course.archive(actor_id=author.id)
        with pytest.raises(AlreadyArchivedError):
            course.archive(actor_id=author.id)

    def test_author_can_unarchive(self) -> None:
        author = make_user()
        course = make_course(author)
        course.archive(actor_id=author.id)
        course.unarchive(actor_id=author.id)
        assert not course.is_archived

    def test_cannot_unarchive_active_course(self) -> None:
        author = make_user()
        course = make_course(author)
        with pytest.raises(NotArchivedError):
            course.unarchive(actor_id=author.id)


class TestCourseChapters:
    def test_add_chapter_increments_index(self) -> None:
        author = make_user()
        course = make_course(author)
        c1 = course.add_chapter(title="Chapter One", body="B" * 30, actor_id=author.id)
        c2 = course.add_chapter(title="Chapter Two", body="B" * 30, actor_id=author.id)
        assert c1.index == 0
        assert c2.index == 1

    def test_non_author_cannot_add_chapter(self) -> None:
        course = make_course()
        with pytest.raises(NotCourseAuthorError):
            course.add_chapter(title="Chapter", body="B" * 30, actor_id=uuid4())

    def test_cannot_add_chapter_to_archived_course(self) -> None:
        author = make_user()
        course = make_course(author)
        course.archive(actor_id=author.id)
        with pytest.raises(ArchivedCourseError):
            course.add_chapter(title="Chapter", body="B" * 30, actor_id=author.id)

    def test_update_chapter(self) -> None:
        author = make_user()
        course = make_course(author)
        chapter = course.add_chapter(title="Old Title", body="B" * 30, actor_id=author.id)
        course.update_chapter(
            actor_id=author.id,
            chapter_id=chapter.id,
            title_str="New Title",
            body_str="C" * 30,
        )
        assert str(course.chapters[0].title) == "New Title"

    def test_update_nonexistent_chapter_raises(self) -> None:
        author = make_user()
        course = make_course(author)
        with pytest.raises(ChapterNotFoundError):
            course.update_chapter(
                actor_id=author.id,
                chapter_id=uuid4(),
                title_str="Title",
                body_str="B" * 30,
            )

    def test_archive_and_unarchive_chapter(self) -> None:
        author = make_user()
        course = make_course(author)
        chapter = course.add_chapter(title="Chapter", body="B" * 30, actor_id=author.id)
        course.archive_chapter(actor_id=author.id, chapter_id=chapter.id)
        assert course.chapters[0].is_archived
        course.unarchive_chapter(actor_id=author.id, chapter_id=chapter.id)
        assert not course.chapters[0].is_archived


class TestCourseEnrollment:
    def test_enroll_user(self) -> None:
        author = make_user()
        course = make_course(author)
        user_id = uuid4()
        course.enroll_user(user_id=user_id)
        assert user_id in course.assignee_ids

    def test_author_cannot_enroll_themselves(self) -> None:
        author = make_user()
        course = make_course(author)
        with pytest.raises(AuthorCannotBeAssigneeError):
            course.enroll_user(user_id=author.id)

    def test_unenroll_user(self) -> None:
        author = make_user()
        course = make_course(author)
        user_id = uuid4()
        course.enroll_user(user_id=user_id)
        course.unenroll_user(user_id=user_id)
        assert user_id not in course.assignee_ids

    def test_unenroll_not_enrolled_is_noop(self) -> None:
        author = make_user()
        course = make_course(author)
        course.unenroll_user(user_id=uuid4())

    def test_cannot_enroll_in_archived_course(self) -> None:
        author = make_user()
        course = make_course(author)
        course.archive(actor_id=author.id)
        with pytest.raises(ArchivedCourseError):
            course.enroll_user(user_id=uuid4())
