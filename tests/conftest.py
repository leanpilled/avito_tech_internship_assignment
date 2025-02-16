import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import AsyncIterator
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from api.auth_utils import get_current_user
from data.db.models.user import UserModel
from settings import settings
from passlib.context import CryptContext

from fastapi.testclient import TestClient
from main import app


class CurrentUser:
    USERNAME = "USERNAME11001"
    PASSWORD = "PASSWORD"


@pytest.fixture(scope="function")
async def current_user(session):
    query = select(UserModel).where(UserModel.username == CurrentUser.USERNAME)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    return user


@pytest.fixture(scope="function")
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(settings.DATABASE_URL)

    async_session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    session = async_session_maker()
    try:
        yield session
    finally:
        await session.close()


@pytest.fixture(scope="session")
@pytest.mark.asyncio
async def client():
    engine = create_async_engine(settings.DATABASE_URL)

    async_session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    session = async_session_maker()

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = UserModel(
        username=CurrentUser.USERNAME,
        password=pwd_context.hash(CurrentUser.PASSWORD),
        balance=1000,
    )
    session.add(user)
    await session.commit()

    app.dependency_overrides[get_current_user] = lambda: user.id
    with TestClient(app) as client:
        yield client
    await session.delete(user)
    await session.commit()
