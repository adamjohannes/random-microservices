from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.course.config import Config

_bearer = HTTPBearer()


def get_config() -> Config:
    return Config()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    config: Config = Depends(get_config),
) -> UUID:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, config.jwt_secret, algorithms=["HS256"])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
        return UUID(sub)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token expired")
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
