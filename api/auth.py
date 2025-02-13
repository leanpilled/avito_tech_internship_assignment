from fastapi import APIRouter, HTTPException
from domain.entities.models import AuthRequest, AuthResponse
from domain.exceptions import InvalidCredentials

from aioinject import Injected
from aioinject.ext.fastapi import inject
from domain.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/")
@inject
async def login_user(
    user: AuthRequest,
    auth_service: Injected[AuthService],
) -> AuthResponse:
    try:
        return await auth_service.login_user(
            username=user.username,
            password=user.password,
        )
    except InvalidCredentials as e:
        raise HTTPException(status_code=409, detail=str(e))
