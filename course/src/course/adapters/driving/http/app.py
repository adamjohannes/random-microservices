from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.course.adapters.driving.http.exception_handlers import (
    authorization_handler,
    domain_validation_handler,
    not_found_handler,
    resource_state_handler,
)
from src.course.adapters.driving.http.dependencies import init_db, init_event_publisher
from src.course.adapters.driving.http.routers.courses import router as courses_router
from src.course.adapters.driving.http.routers.users import router as users_router
from src.course.config import Config
from src.course.domain.exceptions import (
    DomainAuthorizationError,
    DomainValidationError,
    EntityNotFoundError,
    ResourceStateError,
)


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        cfg = Config()
        init_db(cfg)
        await init_event_publisher(cfg)
        yield

    app = FastAPI(title="Course Service", lifespan=lifespan)

    app.add_exception_handler(DomainValidationError, domain_validation_handler)
    app.add_exception_handler(ResourceStateError, resource_state_handler)
    app.add_exception_handler(DomainAuthorizationError, authorization_handler)
    app.add_exception_handler(EntityNotFoundError, not_found_handler)

    app.include_router(users_router)
    app.include_router(courses_router)

    return app
