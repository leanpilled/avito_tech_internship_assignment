import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from data.db.models.user import UserModel
from domain.entities.models import AuthRequest


class UserRepo:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create_user(self, username: str, password: str) -> UserModel:
        user_model = UserModel(
            username=username,
            password=password,
            balance=1000,
        )
        self.session.add(user_model)
        await self.session.commit()
        return user_model

    async def get_user(self, username: str) -> UserModel | None:
        query = select(UserModel).where(
            UserModel.username == username
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def subtract_balance(self, user_id: uuid.UUID, amount: int) -> None:
        query = update(UserModel).where(
            UserModel.id == user_id
        ).values(
            balance = UserModel.balance - amount
        )
        await self.session.execute(query)
        await self.session.commit()

    async def increment_balance(self, user_id: uuid.UUID, amount: int) -> None:
        query = update(UserModel).where(
            UserModel.id == user_id
        ).values(
            balance = UserModel.balance + amount
        )
        await self.session.execute(query)
        await self.session.commit()

    async def get_balance(self, user_id: uuid.UUID) -> int:
        query = select(UserModel.balance).where(
            UserModel.id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar_one()
