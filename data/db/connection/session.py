from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=1800,
)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


class SessionManager:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    def start_transaction(self):
        self.session.begin()

    async def commit_transaction(self):
        await self.session.commit()

    async def rollback_transaction(self):
        await self.session.rollback()


class Base(DeclarativeBase):
    pass
