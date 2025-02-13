import uuid

from fastapi import APIRouter, Depends
from domain.entities.models import InfoResponse

from aioinject import Injected
from aioinject.ext.fastapi import inject
from domain.services.info_service import InfoService
from api.auth_utils import get_current_user

router = APIRouter(prefix="/info", tags=["transaction"])

@router.get("/")
@inject
async def send_coin(
    info_service: Injected[InfoService],
    user_id: uuid.UUID = Depends(get_current_user),
) -> InfoResponse:
    return await info_service.get_info(user_id)
