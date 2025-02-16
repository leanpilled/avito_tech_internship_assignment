import jwt
import uuid
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from typing import Annotated
from domain.entities.models import ErrorResponse
from settings import settings


header_scheme = APIKeyHeader(name="Authorization")


def get_current_user(
    token: Annotated[str, Depends(header_scheme)],
) -> uuid.UUID | JSONResponse:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except InvalidTokenError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(errors="Неавторизован").model_dump(),
        )
    return uuid.UUID(payload.get("user_id"))
