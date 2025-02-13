import jwt
import uuid
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, Depends
from fastapi.security import APIKeyHeader
from typing import Annotated
from settings import settings


header_scheme = APIKeyHeader(name="Authorization")


def get_current_user(token: Annotated[str, Depends(header_scheme)]) -> uuid.UUID:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload.get("user_id")
