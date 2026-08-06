from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.course.config import Config
from src.course.adapters.driven.storage.postgres.repository import (
    PostgresCourseRepository,
    PostgresUserRepository,
)
from src.course.adapters.driven.messaging.rabbitmq_publisher import (
    RabbitMQEventPublisher,
    NoopEventPublisher,
)
from src.course.application.use_cases.course_usecase import CourseUseCase
from src.course.application.use_cases.user_usecase import UserUseCase

_engine = None
_session_factory = None
_event_publisher: RabbitMQEventPublisher | NoopEventPublisher | None = None


def _get_session_factory(config: Config) -> async_sessionmaker:
    global _engine, _session_factory
    if _session_factory is None:
        _engine = create_async_engine(config.database_url)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _session_factory


async def init_event_publisher(config: Config) -> None:
    global _event_publisher
    publisher = RabbitMQEventPublisher(
        host=config.amqp_host,
        user=config.amqp_user,
        password=config.amqp_pass,
    )
    try:
        await publisher.connect()
        _event_publisher = publisher
    except Exception:
        _event_publisher = NoopEventPublisher()


async def get_course_usecase(config: Config) -> AsyncGenerator[CourseUseCase, None]:
    factory = _get_session_factory(config)
    async with factory() as session:
        async with session.begin():
            yield CourseUseCase(
                course_repo=PostgresCourseRepository(session),
                user_repo=PostgresUserRepository(session),
                event_publisher=_event_publisher,
            )


async def get_user_usecase(config: Config) -> AsyncGenerator[UserUseCase, None]:
    factory = _get_session_factory(config)
    async with factory() as session:
        async with session.begin():
            yield UserUseCase(user_repo=PostgresUserRepository(session))
