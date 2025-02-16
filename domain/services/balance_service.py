import uuid
from data.adapters.user_repo import UserRepo


class BalanceService:
    def __init__(self, user_repo: UserRepo) -> None:
        self.user_repo = user_repo

    async def can_afford(
        self,
        user_id: uuid.UUID,
        amount: int,
    ) -> bool:
        current_balance = await self.user_repo.get_balance(user_id)
        if current_balance < amount:
            return False
        return True

    async def conduct_deal_payment(
        self,
        user_id: uuid.UUID,
        amount: int,
    ):
        await self.user_repo.subtract_balance(user_id, amount)

    async def conduct_transaction_fund_transfer(
        self,
        from_user: uuid.UUID,
        to_user: uuid.UUID,
        amount: int,
    ):
        await self.user_repo.subtract_balance(from_user, amount)
        await self.user_repo.increment_balance(to_user, amount)
