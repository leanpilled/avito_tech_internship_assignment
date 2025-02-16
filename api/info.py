import uuid

from fastapi import APIRouter, Depends
from api.base_responses import BASE_RESPONSES
from domain.entities.models import InfoResponse

from aioinject import Injected
from aioinject.ext.fastapi import inject
from domain.services.info_service import InfoService
from api.auth_utils import get_current_user

router = APIRouter(prefix="/info", tags=["info"])


@router.get(
    "/",
    summary="Получить информацию о монетах, инвентаре и истории транзакций.",
    responses={
        **BASE_RESPONSES,
        200: {
            "description": "Успешный ответ",
            "model": InfoResponse,
        },
    },
)
@inject
async def send_coin(
    info_service: Injected[InfoService],
    user_id: uuid.UUID = Depends(get_current_user),
) -> InfoResponse:
    return await info_service.get_info(user_id)
