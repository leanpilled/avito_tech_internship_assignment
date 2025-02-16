import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.models import AuthRequest
from main import app

pytestmark = [pytest.mark.asyncio]
from typing import AsyncIterator

from sqlalchemy import select

# from data.db.connection.session import async_session_maker, get_session
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from data.db.models.user import UserModel
from settings import settings


@pytest.fixture
async def get_session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(settings.DATABASE_URL)

    async_session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_maker() as session:
        yield session

client = TestClient(app)

@pytest.mark.asyncio
async def test_auth(get_session):
    response = client.post(
        "/auth/",
        json=AuthRequest(
            username="zaza190",
            password="zaza190",
        ).model_dump()
    )

    query = select(UserModel).where(
        UserModel.username == "zaza190"
    )
    result = await get_session.execute(query)
    user = result.scalar_one_or_none()

    assert user
    assert response.status_code == 200
