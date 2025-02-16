import uuid

from data.adapters.deal_repo import DealRepo
from data.adapters.user_repo import UserRepo
from data.adapters.transaction_repo import TransactionRepo
from domain.entities.models import CoinHistory, InfoResponse


class InfoService:
    def __init__(
        self,
        user_repo: UserRepo,
        deal_repo: DealRepo,
        transaction_repo: TransactionRepo,
    ) -> None:
        self.user_repo = user_repo
        self.deal_repo = deal_repo
        self.transaction_repo = transaction_repo

    async def get_info(
        self,
        user_id: uuid.UUID,
    ) -> InfoResponse:
        balance = await self.user_repo.get_balance(user_id)
        received_coins = (
            await self.transaction_repo.get_incoming_transactions_by_user_id(user_id)
        )
        send_coins = await self.transaction_repo.get_outgoing_transactions_by_user_id(
            user_id
        )
        inventory = await self.deal_repo.get_items_by_user_id(user_id)
        return InfoResponse(
            coins=balance,
            inventory=inventory,
            coin_history=CoinHistory(
                received=received_coins,
                send=send_coins,
            ),
        )
