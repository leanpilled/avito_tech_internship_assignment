import uuid

from sqlalchemy import select, func

from data.db.connection.session import SessionManager
from data.db.models.deal import DealModel
from data.db.models.item import ItemModel
from domain.entities.models import Item


class DealRepo:
    def __init__(
        self,
        session_manager: SessionManager,
    ) -> None:
        self.session = session_manager.session

    async def create_deal(self, user_id: uuid.UUID, item_id: uuid.UUID) -> DealModel:
        deal_model = DealModel(
            user_id=user_id,
            item_id=item_id,
        )
        self.session.add(deal_model)
        await self.session.flush()
        return deal_model

    async def get_items_by_user_id(self, user_id: uuid.UUID) -> list[Item | None]:
        query = (
            select(
                ItemModel.type,
                func.count().label("quantity"),
            )
            .join(DealModel, DealModel.item_id == ItemModel.id)
            .where(DealModel.user_id == user_id)
            .group_by(ItemModel.type)
        )

        result = (await self.session.execute(query)).mappings().all()

        items = []
        for row in result:
            items.append(Item.model_validate(row, from_attributes=True))

        return items
