from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from api.base_responses import BASE_RESPONSES
from domain.entities.models import AuthRequest, AuthResponse, ErrorResponse
from domain.exceptions import InvalidCredentials

from aioinject import Injected
from aioinject.ext.fastapi import inject
from domain.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/",
    summary="Аутентификация и получение JWT-токена.",
    responses={
        **BASE_RESPONSES,
        200: {
            "description": "Успешная аутентификация.",
            "model": AuthResponse,
        },
        409: {
            "description": "Конфликт.",
            "model": ErrorResponse,
        }
    },
)
@inject
async def login_user(
    user: AuthRequest,
    auth_service: Injected[AuthService],
):
    try:
        return await auth_service.login_user(
            username=user.username,
            password=user.password,
        )
    except InvalidCredentials:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                errors="Неверный логин или пароль."
            ).model_dump()
        )
