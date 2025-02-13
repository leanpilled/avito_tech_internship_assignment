import uuid

from data.adapters.user_repo import UserRepo
from data.adapters.deal_repo import DealRepo
from data.adapters.item_repo import ItemRepo
from domain.services.balance_service import BalanceService

from domain.exceptions import InsufficientFunds


class DealService:
    def __init__(
        self,
        deal_repo: DealRepo,
        user_repo: UserRepo,
        item_repo: ItemRepo,
        balance_service: BalanceService,
    ) -> None:
        self.deal_repo = deal_repo
        self.user_repo = user_repo
        self.item_repo = item_repo
        self.balance_service = balance_service

    async def conduct_deal(self, user_id: uuid.UUID, item_type: str) -> None:
        item = await self.item_repo.get_item_by_type(item_type)
        can_afford = await self.balance_service.can_afford(user_id, item.price)
        if not can_afford:
            raise InsufficientFunds
        await self.balance_service.conduct_deal_payment(user_id, item.price)
        await self.deal_repo.create_deal(user_id, item.id)
