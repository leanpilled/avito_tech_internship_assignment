from enum import StrEnum

import pytest
from passlib.context import CryptContext
from sqlalchemy import select

from api.auth_utils import get_current_user
from data.db.models.user import UserModel
from domain.entities.models import AuthRequest


class User(StrEnum):
    USERNAME = "USERNAME11"
    PASSWORD = "PASSWORD"
    WRONG_PASSWORD = "WRONG_PASSWORD"


@pytest.fixture
async def get_existing_user(session):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = UserModel(
        username=User.USERNAME,
        password=pwd_context.hash(User.PASSWORD),
        balance=1000,
    )
    session.add(user)
    await session.commit()
    yield user
    await session.delete(user)
    await session.commit()


@pytest.mark.asyncio
async def test_login_existing_user(client, get_existing_user):
    user = get_existing_user
    response = client.post(
        "/auth/",
        json=AuthRequest(
            username=User.USERNAME,
            password=User.PASSWORD,
        ).model_dump(),
    )
    assert response.status_code == 200
    assert user.id == get_current_user(response.json()["token"])


@pytest.mark.asyncio
async def test_login_non_existing_user(client, session):
    response = client.post(
        "/auth/",
        json=AuthRequest(
            username=User.USERNAME,
            password=User.PASSWORD,
        ).model_dump(),
    )
    assert response.status_code == 200

    query = select(UserModel).where(UserModel.username == User.USERNAME)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    assert user.id == get_current_user(response.json()["token"])

    await session.delete(user)
    await session.commit()


@pytest.mark.asyncio
async def test_login_wrong_credentials(client, get_existing_user):
    response = client.post(
        "/auth/",
        json=AuthRequest(
            username=User.USERNAME,
            password=User.WRONG_PASSWORD,
        ).model_dump(),
    )
    assert response.status_code == 409
