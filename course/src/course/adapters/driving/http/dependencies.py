from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.course.config import Config
from src.course.adapters.driven.storage.postgres.repository import (
    PostgresCourseRepository,
    PostgresUserRepository,
)
from src.course.application.use_cases.course_usecase import CourseUseCase
from src.course.application.use_cases.user_usecase import UserUseCase

_engine = None
_session_factory = None


def _get_session_factory(config: Config) -> async_sessionmaker:
    global _engine, _session_factory
    if _session_factory is None:
        _engine = create_async_engine(config.database_url)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _session_factory


async def get_course_usecase(config: Config) -> AsyncGenerator[CourseUseCase, None]:
    factory = _get_session_factory(config)
    async with factory() as session:
        async with session.begin():
            yield CourseUseCase(
                course_repo=PostgresCourseRepository(session),
                user_repo=PostgresUserRepository(session),
            )


async def get_user_usecase(config: Config) -> AsyncGenerator[UserUseCase, None]:
    factory = _get_session_factory(config)
    async with factory() as session:
        async with session.begin():
            yield UserUseCase(user_repo=PostgresUserRepository(session))
