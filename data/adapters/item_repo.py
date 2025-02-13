from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.db.models.item import ItemModel
from domain.entities.models import ItemDto


class ItemRepo:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def get_item_by_type(self, item_type: str) -> ItemDto | None:
        query = select(
            ItemModel,
        ).where(
            ItemModel.type == item_type
        )

        result = (await self.session.execute(query)).mappings().all()

        return ItemDto.model_validate(
            result,
            from_attributes=True
        )
