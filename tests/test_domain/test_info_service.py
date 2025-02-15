import unittest
from unittest.mock import AsyncMock
import uuid

from data.adapters.deal_repo import DealRepo
from data.adapters.transaction_repo import TransactionRepo
from data.adapters.user_repo import UserRepo
from domain.entities.models import InfoResponse, Item, ReceivedCoin, SendCoin
from domain.services.info_service import InfoService


class TestInfoService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_user_repo = AsyncMock(spec=UserRepo)
        self.mock_deal_repo = AsyncMock(spec=DealRepo)
        self.mock_transaction_repo = AsyncMock(spec=TransactionRepo)
        self.info_service = InfoService(
            self.mock_user_repo,
            self.mock_deal_repo,
            self.mock_transaction_repo,
        )
        self.user_id = uuid.uuid4()
        self.balance = 100
        self.received_coins = [
            ReceivedCoin(
                from_user="user1",
                amount=100,
            ),
            ReceivedCoin(
                from_user="user2",
                amount=1000,
            ),
        ]
        self.send_coins = [
            SendCoin(
                to_user="user1",
                amount=100
            ),
            SendCoin(
                to_user="user2",
                amount=1000,
            ),
        ]
        self.inventory = [
            Item(
                type="cup",
                quantity=2,
            ),
        ]

    async def test_get_info(self):
        self.mock_user_repo.get_balance.return_value = self.balance
        self.mock_transaction_repo.get_incoming_transactions_by_user_id.return_value = self.received_coins
        self.mock_transaction_repo.get_outgoing_transactions_by_user_id.return_value = self.send_coins
        self.mock_deal_repo.get_items_by_user_id.return_value = self.inventory

        response = await self.info_service.get_info(self.user_id)

        self.mock_user_repo.get_balance.assert_called_once_with(self.user_id)
        self.mock_transaction_repo.get_incoming_transactions_by_user_id.assert_called_once_with(self.user_id)
        self.mock_transaction_repo.get_outgoing_transactions_by_user_id.assert_called_once_with(self.user_id)
        self.mock_deal_repo.get_items_by_user_id.assert_called_once_with(self.user_id)

        self.assertIsInstance(response, InfoResponse)
        self.assertEqual(response.coins, self.balance)
        self.assertEqual(response.inventory, self.inventory)
        self.assertEqual(response.coin_history.received, self.received_coins)
        self.assertEqual(response.coin_history.send, self.send_coins)