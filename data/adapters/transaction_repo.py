import uuid

from sqlalchemy import select

from data.db.connection.session import SessionManager
from data.db.models.transaction import TransactionModel
from data.db.models.user import UserModel
from domain.entities.models import ReceivedCoin, SendCoin


class TransactionRepo:
    def __init__(
        self,
        session_manager: SessionManager,
    ) -> None:
        self.session = session_manager.session

    async def create_transaction(
        self, from_user: uuid.UUID, to_user: uuid.UUID, amount: int
    ) -> TransactionModel:
        transaction_model = TransactionModel(
            user_from_id=from_user,
            user_to_id=to_user,
            amount=amount,
        )
        self.session.add(transaction_model)
        await self.session.flush()
        return transaction_model

    async def get_incoming_transactions_by_user_id(
        self, user_id: uuid.UUID
    ) -> list[ReceivedCoin | None]:
        query = (
            select(
                TransactionModel.amount,
                UserModel.username,
            )
            .join(
                UserModel, UserModel.id == TransactionModel.user_from_id, isouter=True
            )
            .where(TransactionModel.user_to_id == user_id)
        )

        result = (await self.session.execute(query)).mappings().all()

        incoming_transactions = []
        for row in result:
            incoming_transactions.append(
                ReceivedCoin(
                    from_user=row.username,
                    amount=row.amount,
                )
            )

        return incoming_transactions

    async def get_outgoing_transactions_by_user_id(
        self, user_id: uuid.UUID
    ) -> list[SendCoin | None]:
        query = (
            select(
                TransactionModel.amount,
                UserModel.username,
            )
            .join(UserModel, UserModel.id == TransactionModel.user_to_id, isouter=True)
            .where(TransactionModel.user_from_id == user_id)
        )

        result = (await self.session.execute(query)).mappings().all()

        outgoing_transactions = []
        for row in result:
            outgoing_transactions.append(
                SendCoin(
                    to_user=row.username,
                    amount=row.amount,
                )
            )

        return outgoing_transactions
