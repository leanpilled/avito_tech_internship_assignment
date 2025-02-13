import uuid

from fastapi import APIRouter, Depends
from domain.exceptions import InsufficientFunds

from aioinject import Injected
from aioinject.ext.fastapi import inject
from domain.services.deal_service import DealService

from api.auth_utils import get_current_user

router = APIRouter(prefix="/buy", tags=["deal"])

@router.get("/{item}")
@inject
async def buy_item(
    item: str,
    deal_service: Injected[DealService],
    user_id: uuid.UUID = Depends(get_current_user),
) -> None:
    try:
        await deal_service.conduct_deal(user_id, item)
    except InsufficientFunds:
        ...
