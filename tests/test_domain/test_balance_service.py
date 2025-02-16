import unittest
import uuid
from unittest.mock import AsyncMock

from data.adapters.user_repo import UserRepo
from domain.services.balance_service import BalanceService


class TestBalanceService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_user_repo = AsyncMock(spec=UserRepo)
        self.balance_service = BalanceService(self.mock_user_repo)
        self.user_id = uuid.uuid4()
        self.balance = 100
        self.affordable_amount = self.balance - 1
        self.not_affordable_amount = self.balance + 1

    async def test_can_afford(self):
        self.mock_user_repo.get_balance.return_value = self.balance

        result = await self.balance_service.can_afford(
            self.user_id, self.affordable_amount
        )
        self.mock_user_repo.get_balance.assert_called_once_with(self.user_id)
        self.assertTrue(result)

        result = await self.balance_service.can_afford(self.user_id, 150)
        self.assertFalse(result)

    async def test_conduct_deal_payment(self):
        await self.balance_service.conduct_deal_payment(
            self.user_id, self.affordable_amount
        )
        self.mock_user_repo.subtract_balance.assert_called_once_with(
            self.user_id, self.affordable_amount
        )

    async def test_conduct_transaction_fund_transfer(self):
        from_user = uuid.uuid4()
        to_user = uuid.uuid4()

        await self.balance_service.conduct_transaction_fund_transfer(
            from_user, to_user, self.affordable_amount
        )

        self.mock_user_repo.subtract_balance.assert_called_once_with(
            from_user, self.affordable_amount
        )
        self.mock_user_repo.increment_balance.assert_called_once_with(
            to_user, self.affordable_amount
        )
