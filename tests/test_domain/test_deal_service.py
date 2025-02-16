import unittest
from unittest.mock import AsyncMock, MagicMock
import uuid

from data.adapters.deal_repo import DealRepo
from data.adapters.item_repo import ItemRepo
from data.adapters.user_repo import UserRepo
from data.db.connection.session import SessionManager
from domain.exceptions import InsufficientFunds, ItemDoesntExists
from domain.services.balance_service import BalanceService
from domain.services.deal_service import DealService


class TestDealService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_deal_repo = AsyncMock(spec=DealRepo)
        self.mock_user_repo = AsyncMock(spec=UserRepo)
        self.mock_item_repo = AsyncMock(spec=ItemRepo)
        self.mock_balance_service = AsyncMock(spec=BalanceService)
        self.mock_session_manager = AsyncMock(spec=SessionManager)
        self.deal_service = DealService(
            self.mock_deal_repo,
            self.mock_user_repo,
            self.mock_item_repo,
            self.mock_balance_service,
            self.mock_session_manager,
        )
        self.user_id = uuid.uuid4()

    async def test_conduct_deal_success(self):
        item_type = "test_item"
        item = MagicMock()
        item.id = uuid.uuid4()
        item.price = 50

        self.mock_item_repo.get_item_by_type.return_value = item
        self.mock_balance_service.can_afford.return_value = True

        await self.deal_service.conduct_deal(self.user_id, item_type)

        self.mock_item_repo.get_item_by_type.assert_called_once_with(item_type)
        self.mock_session_manager.start_transaction.assert_called_once()
        self.mock_balance_service.can_afford.assert_called_once_with(
            self.user_id, item.price
        )
        self.mock_deal_repo.create_deal.assert_called_once_with(self.user_id, item.id)
        self.mock_balance_service.conduct_deal_payment.assert_called_once_with(
            self.user_id, item.price
        )
        self.mock_session_manager.commit_transaction.assert_called_once()

    async def test_conduct_deal_insufficient_funds(self):
        item_type = "test_item"
        item = MagicMock()
        item.price = 100

        self.mock_item_repo.get_item_by_type.return_value = item
        self.mock_balance_service.can_afford.return_value = False

        with self.assertRaises(InsufficientFunds):
            await self.deal_service.conduct_deal(self.user_id, item_type)

    async def test_conduct_deal_item_does_not_exist(self):
        item_type = "nonexistent_item"
        self.mock_item_repo.get_item_by_type.return_value = None

        with self.assertRaises(ItemDoesntExists):
            await self.deal_service.conduct_deal(self.user_id, item_type)
