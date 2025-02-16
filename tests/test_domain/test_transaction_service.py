import unittest
from unittest.mock import AsyncMock, MagicMock
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
from domain.services.transaction_service import TransactionService


class TestTransactionService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_user_repo = AsyncMock(spec=UserRepo)
        self.mock_item_repo = AsyncMock(spec=ItemRepo)
        self.mock_transaction_repo = AsyncMock(spec=TransactionRepo)
        self.mock_balance_service = AsyncMock(spec=BalanceService)
        self.mock_session_manager = AsyncMock(spec=SessionManager)
        self.transaction_service = TransactionService(
            self.mock_user_repo,
            self.mock_item_repo,
            self.mock_transaction_repo,
            self.mock_balance_service,
            self.mock_session_manager,
        )
        self.from_user_id = uuid.uuid4()
        self.to_user_id = uuid.uuid4()
        self.positive_amount = 50
        self.negative_amount = -50

    async def test_conduct_transaction_success(self):
        to_user = MagicMock()
        to_user.id = self.to_user_id

        self.mock_user_repo.get_user.return_value = to_user
        self.mock_balance_service.can_afford.return_value = True

        await self.transaction_service.conduct_transaction(
            self.from_user_id, "receiver_user", self.positive_amount
        )

        self.mock_user_repo.get_user.assert_called_once_with("receiver_user")
        self.mock_session_manager.start_transaction.assert_called_once()
        self.mock_balance_service.can_afford.assert_called_once_with(
            self.from_user_id, self.positive_amount
        )
        self.mock_transaction_repo.create_transaction.assert_called_once_with(
            self.from_user_id, self.to_user_id, self.positive_amount
        )
        self.mock_balance_service.conduct_transaction_fund_transfer.assert_called_once_with(
            self.from_user_id, self.to_user_id, self.positive_amount
        )
        self.mock_session_manager.commit_transaction.assert_called_once()

    async def test_conduct_transaction_negative_amount(self):
        with self.assertRaises(NegativeTransactionAmount):
            await self.transaction_service.conduct_transaction(
                self.from_user_id, "receiver_user", self.negative_amount
            )

    async def test_conduct_transaction_user_does_not_exist(self):
        self.mock_user_repo.get_user.return_value = None

        with self.assertRaises(UserDoesntExists):
            await self.transaction_service.conduct_transaction(
                self.from_user_id, "non_existent_user", self.positive_amount
            )

    async def test_conduct_transaction_self_transfer(self):
        to_user = MagicMock()
        to_user.id = self.from_user_id
        self.mock_user_repo.get_user.return_value = to_user

        with self.assertRaises(IncorrectReceiverCredential):
            await self.transaction_service.conduct_transaction(
                self.from_user_id, "self", self.positive_amount
            )

    async def test_conduct_transaction_insufficient_funds(self):
        to_user = MagicMock()
        to_user.id = self.to_user_id

        self.mock_user_repo.get_user.return_value = to_user
        self.mock_balance_service.can_afford.return_value = False

        with self.assertRaises(InsufficientFunds):
            await self.transaction_service.conduct_transaction(
                self.from_user_id, "receiver_user", 50
            )
