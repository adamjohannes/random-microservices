from fastapi import Request
from fastapi.responses import JSONResponse

from src.course.domain.exceptions import (
    DomainValidationError,
    ResourceStateError,
    DomainAuthorizationError,
    EntityNotFoundError,
)


async def domain_validation_handler(request: Request, exc: DomainValidationError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def resource_state_handler(request: Request, exc: ResourceStateError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def authorization_handler(request: Request, exc: DomainAuthorizationError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


async def not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})
