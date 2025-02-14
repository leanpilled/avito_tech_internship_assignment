import uuid

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from domain.entities.models import ErrorResponse, SendCoinRequest
from domain.exceptions import InsufficientFunds

from aioinject import Injected
from aioinject.ext.fastapi import inject
from domain.services.transaction_service import TransactionService
from api.auth_utils import get_current_user

router = APIRouter(tags=["transaction"])

@router.post("/sendCoin", responses={200: {"description": "Успешный ответ"}})
@inject
async def send_coin(
    send_coin_request: SendCoinRequest,
    transaction_service: Injected[TransactionService],
    user_id: uuid.UUID = Depends(get_current_user),
) -> ErrorResponse | None:
    try:
        await transaction_service.conduct_transaction(
            from_user_id=user_id,
            to_user_login=send_coin_request.to_user,
            amount=send_coin_request.amount,
        )
    except InsufficientFunds:
        return Response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                errors="Недостаточно средств"
            )
        )
