import uuid

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from api.base_responses import BASE_RESPONSES
from domain.entities.models import ErrorResponse
from domain.exceptions import InsufficientFunds, ItemDoesntExists

from aioinject import Injected
from aioinject.ext.fastapi import inject
from domain.services.deal_service import DealService

from api.auth_utils import get_current_user

router = APIRouter(prefix="/buy", tags=["deal"])


@router.get(
    "/{item}",
    summary="Купить предмет за монеты.",
    responses=BASE_RESPONSES,
)
@inject
async def buy_item(
    item: str,
    deal_service: Injected[DealService],
    user_id: uuid.UUID = Depends(get_current_user),
):
    try:
        await deal_service.conduct_deal(user_id, item)
    except InsufficientFunds:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(errors="Недостаточно средств").model_dump(),
        )
    except ItemDoesntExists:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(errors="Такого товара не сущетсвует").model_dump(),
        )
