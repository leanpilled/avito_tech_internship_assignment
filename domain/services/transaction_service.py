import uuid

from data.adapters.item_repo import ItemRepo
from data.adapters.transaction_repo import TransactionRepo
from data.adapters.user_repo import UserRepo
from data.db.connection.session import SessionManager
from domain.exceptions import (
    IncorrectReceiverCredential,
    InsufficientFunds,
    NegativeTransactionAmount,
    UserDoesntExists,
)
from domain.services.balance_service import BalanceService


class TransactionService:
    def __init__(
        self,
        user_repo: UserRepo,
        item_repo: ItemRepo,
        transaction_repo: TransactionRepo,
        balance_service: BalanceService,
        session_manager: SessionManager,
    ) -> None:
        self.user_repo = user_repo
        self.item_repo = item_repo
        self.transaction_repo = transaction_repo
        self.balance_service = balance_service
        self.session_manager = session_manager

    async def conduct_transaction(
        self, from_user_id: uuid.UUID, to_user_login: str, amount: int
    ) -> None:
        if amount <= 0:
            raise NegativeTransactionAmount

        to_user = await self.user_repo.get_user(to_user_login)
        if not to_user:
            raise UserDoesntExists

        if from_user_id.int == to_user.id.int:
            raise IncorrectReceiverCredential

        self.session_manager.start_transaction()

        can_afford = await self.balance_service.can_afford(from_user_id, amount)
        if not can_afford:
            raise InsufficientFunds

        await self.transaction_repo.create_transaction(
            from_user_id,
            to_user.id,
            amount,
        )
        await self.balance_service.conduct_transaction_fund_transfer(
            from_user_id,
            to_user.id,
            amount,
        )

        await self.session_manager.commit_transaction()
