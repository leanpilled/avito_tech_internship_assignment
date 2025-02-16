from sqlalchemy import select

from data.db.connection.session import SessionManager
from data.db.models.item import ItemModel
from domain.entities.models import ItemDto


class ItemRepo:
    def __init__(
        self,
        session_manager: SessionManager,
    ) -> None:
        self.session = session_manager.session

    async def get_item_by_type(self, item_type: str) -> ItemDto | None:
        query = select(
            ItemModel,
        ).where(ItemModel.type == item_type)

        result = (await self.session.execute(query)).scalar_one_or_none()

        if not result:
            return None

        return ItemDto.model_validate(result, from_attributes=True)
