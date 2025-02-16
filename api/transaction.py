import uuid

from aioinject import Injected
from aioinject.ext.fastapi import inject
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from api.auth_utils import get_current_user
from api.base_responses import BASE_RESPONSES
from domain.entities.models import ErrorResponse, SendCoinRequest
from domain.exceptions import (
    IncorrectReceiverCredential,
    InsufficientFunds,
    NegativeTransactionAmount,
    UserDoesntExists,
)
from domain.services.transaction_service import TransactionService

router = APIRouter(tags=["transaction"])


@router.post(
    "/sendCoin",
    summary="Отправить монеты другому пользователю.",
    responses=BASE_RESPONSES,
)
@inject
async def send_coin(
    send_coin_request: SendCoinRequest,
    transaction_service: Injected[TransactionService],
    user_id: uuid.UUID = Depends(get_current_user),
):
    try:
        await transaction_service.conduct_transaction(
            from_user_id=user_id,
            to_user_login=send_coin_request.to_user,
            amount=send_coin_request.amount,
        )
    except InsufficientFunds:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(errors="Недостаточно средств").model_dump(),
        )
    except UserDoesntExists:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                errors="Такого пользователя не сущетсвует"
            ).model_dump(),
        )
    except NegativeTransactionAmount:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                errors="Сумма транзакции должна быть больше нуля"
            ).model_dump(),
        )
    except IncorrectReceiverCredential:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(
                errors="Невозможно отправить монетки этому пользователю"
            ).model_dump(),
        )
