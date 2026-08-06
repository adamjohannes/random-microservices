from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.course.adapters.driven.storage.postgres.models import Base
from src.course.adapters.driven.storage.postgres.repository import (
    PostgresCourseRepository,
    PostgresUserRepository,
)
from src.course.domain.course import Course
from src.course.domain.user import User
from src.course.domain.user_name import UserName


DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/course_test_db"


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session(engine) -> AsyncSession:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        async with s.begin():
            yield s
            await s.rollback()


@pytest.fixture
def user_repo(session: AsyncSession) -> PostgresUserRepository:
    return PostgresUserRepository(session)


@pytest.fixture
def course_repo(session: AsyncSession) -> PostgresCourseRepository:
    return PostgresCourseRepository(session)


def make_user(name: str = "Adam Johannes", email: str | None = None) -> User:
    return User.create(
        account_id=uuid4(),
        name_str=name,
        email_str=email or f"{uuid4()}@example.com",
    )


def make_course(author: User) -> Course:
    return Course.create(
        author=author,
        title_str="Introduction to Testing",
        description="A thorough introduction to software testing practices and tools.",
    )


class TestPostgresUserRepository:
    async def test_save_and_get_by_id(self, user_repo: PostgresUserRepository) -> None:
        user = make_user()
        await user_repo.save(user)
        fetched = await user_repo.get_by_id(user.id)
        assert fetched is not None
        assert fetched.id == user.id
        assert str(fetched.name) == str(user.name)
        assert str(fetched.email) == str(user.email)

    async def test_get_by_id_returns_none_when_missing(self, user_repo: PostgresUserRepository) -> None:
        result = await user_repo.get_by_id(uuid4())
        assert result is None

    async def test_save_is_idempotent(self, user_repo: PostgresUserRepository) -> None:
        user = make_user()
        await user_repo.save(user)
        user.update_name(UserName("New Name"))
        await user_repo.save(user)
        fetched = await user_repo.get_by_id(user.id)
        assert fetched is not None
        assert str(fetched.name) == "New Name"


class TestPostgresCourseRepository:
    async def test_save_and_get_by_id(
        self, user_repo: PostgresUserRepository, course_repo: PostgresCourseRepository
    ) -> None:
        author = make_user()
        await user_repo.save(author)
        course = make_course(author)
        await course_repo.save(course)

        fetched = await course_repo.get_by_id(course.id)
        assert fetched is not None
        assert fetched.id == course.id
        assert str(fetched.title) == str(course.title)

    async def test_get_by_id_returns_none_when_missing(self, course_repo: PostgresCourseRepository) -> None:
        result = await course_repo.get_by_id(uuid4())
        assert result is None

    async def test_save_with_chapters(
        self, user_repo: PostgresUserRepository, course_repo: PostgresCourseRepository
    ) -> None:
        author = make_user()
        await user_repo.save(author)
        course = make_course(author)
        course.add_chapter(title="Chapter One", body="B" * 30, actor_id=author.id)
        await course_repo.save(course)

        fetched = await course_repo.get_by_id(course.id)
        assert fetched is not None
        assert len(fetched.chapters) == 1
        assert str(fetched.chapters[0].title) == "Chapter One"

    async def test_get_by_author_id(
        self, user_repo: PostgresUserRepository, course_repo: PostgresCourseRepository
    ) -> None:
        author = make_user()
        await user_repo.save(author)
        course = make_course(author)
        await course_repo.save(course)

        results = await course_repo.get_by_author_id(author.id)
        assert any(c.id == course.id for c in results)

    async def test_get_by_assignee_id(
        self, user_repo: PostgresUserRepository, course_repo: PostgresCourseRepository
    ) -> None:
        author = make_user()
        assignee = make_user(name="Jane Doe")
        await user_repo.save(author)
        await user_repo.save(assignee)
        course = make_course(author)
        course.enroll_user(user_id=assignee.id)
        await course_repo.save(course)

        results = await course_repo.get_by_assignee_id(assignee.id)
        assert any(c.id == course.id for c in results)
