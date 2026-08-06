from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.course.application.use_cases.course_usecase import CourseUseCase
from src.course.domain.course import Course
from src.course.domain.exceptions import CourseNotFoundError, UserNotFoundError
from src.course.domain.user import User


def make_user() -> User:
    return User.create(account_id=uuid4(), name_str="Adam Johannes", email_str="adam@example.com")


def make_course(author: User) -> Course:
    return Course.create(
        author=author,
        title_str="Introduction to Testing",
        description="A thorough introduction to software testing practices and tools.",
    )


@pytest.fixture
def author() -> User:
    return make_user()


@pytest.fixture
def course(author: User) -> Course:
    return make_course(author)


@pytest.fixture
def course_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def user_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def usecase(course_repo: AsyncMock, user_repo: AsyncMock) -> CourseUseCase:
    return CourseUseCase(course_repo=course_repo, user_repo=user_repo)


class TestCreateCourse:
    async def test_creates_course_for_existing_user(
        self, usecase: CourseUseCase, course_repo: AsyncMock, user_repo: AsyncMock, author: User
    ) -> None:
        user_repo.get_by_id.return_value = author
        course_repo.save.return_value = None

        result = await usecase.create_course(
            actor_id=author.id,
            title="Introduction to Testing",
            description="A thorough introduction to software testing practices and tools.",
        )

        user_repo.get_by_id.assert_awaited_once_with(author.id)
        course_repo.save.assert_awaited_once()
        assert str(result.title) == "Introduction to Testing"

    async def test_raises_when_user_not_found(
        self, usecase: CourseUseCase, user_repo: AsyncMock
    ) -> None:
        user_repo.get_by_id.return_value = None
        with pytest.raises(UserNotFoundError):
            await usecase.create_course(actor_id=uuid4(), title="Title", description="D" * 30)


class TestRetrieveCourse:
    async def test_returns_course(
        self, usecase: CourseUseCase, course_repo: AsyncMock, course: Course
    ) -> None:
        course_repo.get_by_id.return_value = course
        result = await usecase.retrieve_course(course_id=course.id)
        assert result.id == course.id

    async def test_raises_when_not_found(
        self, usecase: CourseUseCase, course_repo: AsyncMock
    ) -> None:
        course_repo.get_by_id.return_value = None
        with pytest.raises(CourseNotFoundError):
            await usecase.retrieve_course(course_id=uuid4())


class TestEnrollUser:
    async def test_enrolls_user(
        self,
        usecase: CourseUseCase,
        course_repo: AsyncMock,
        user_repo: AsyncMock,
        course: Course,
    ) -> None:
        enrollee = make_user()
        course_repo.get_by_id.return_value = course
        user_repo.get_by_id.return_value = enrollee

        await usecase.enroll_user_in_course(user_id=enrollee.id, course_id=course.id)

        assert enrollee.id in course.assignee_ids
        course_repo.save.assert_awaited_once()

    async def test_raises_when_user_not_found(
        self,
        usecase: CourseUseCase,
        course_repo: AsyncMock,
        user_repo: AsyncMock,
        course: Course,
    ) -> None:
        course_repo.get_by_id.return_value = course
        user_repo.get_by_id.return_value = None
        with pytest.raises(UserNotFoundError):
            await usecase.enroll_user_in_course(user_id=uuid4(), course_id=course.id)


class TestArchiveCourse:
    async def test_archives_course(
        self,
        usecase: CourseUseCase,
        course_repo: AsyncMock,
        author: User,
        course: Course,
    ) -> None:
        course_repo.get_by_id.return_value = course
        await usecase.archive_course(actor_id=author.id, course_id=course.id)
        assert course.is_archived
        course_repo.save.assert_awaited_once()
