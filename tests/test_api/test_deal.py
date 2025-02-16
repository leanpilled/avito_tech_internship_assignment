import pytest
from sqlalchemy import and_, select

from data.db.models.deal import DealModel
from data.db.models.item import ItemModel


class TestVariables:
    ITEM_TYPE = "ITEM_TYPE"
    CHEAP_ITEM_PRICE = 10
    EXPENSIVE_ITEM_PRICE = 10000
    NON_EXISTING_ITEM = "NON_EXISTING_ITEM"


@pytest.fixture
async def get_cheap_item(session):
    item = ItemModel(
        type=TestVariables.ITEM_TYPE,
        price=TestVariables.CHEAP_ITEM_PRICE,
    )
    session.add(item)
    await session.commit()
    yield item
    await session.delete(item)
    await session.commit()


@pytest.fixture
async def get_expensive_item(session):
    item = ItemModel(
        type=TestVariables.ITEM_TYPE,
        price=TestVariables.EXPENSIVE_ITEM_PRICE,
    )
    session.add(item)
    await session.commit()
    yield item
    await session.delete(item)
    await session.commit()


async def test_conduct_deal(client, session, current_user, get_cheap_item):
    before_deal_balance = current_user.balance

    response = client.get(f"/buy/{get_cheap_item.type}")
    assert response.status_code == 200
    query = select(DealModel).where(
        and_(
            DealModel.user_id == current_user.id,
            DealModel.item_id == get_cheap_item.id,
        )
    )
    result = await session.execute(query)
    deal = result.scalar_one_or_none()
    assert deal
    await session.refresh(current_user)
    assert current_user.balance == before_deal_balance - TestVariables.CHEAP_ITEM_PRICE

    await session.delete(deal)
    await session.commit()


async def test_conduct_deal_insufficient_funds(
    client, session, current_user, get_expensive_item
):
    before_deal_balance = current_user.balance

    response = client.get(f"/buy/{get_expensive_item.type}")
    assert response.status_code == 400
    assert response.json()["errors"] == "Недостаточно средств"
    query = select(DealModel).where(
        and_(
            DealModel.user_id == current_user.id,
            DealModel.item_id == get_expensive_item.id,
        )
    )
    result = await session.execute(query)
    deal = result.scalar_one_or_none()
    assert not deal

    await session.refresh(current_user)
    assert current_user.balance == before_deal_balance


async def test_conduct_deal_non_existing_item(client, session, current_user):
    before_deal_balance = current_user.balance

    response = client.get(f"/buy/{TestVariables.NON_EXISTING_ITEM}")
    assert response.status_code == 422
    assert response.json()["errors"] == "Такого товара не сущетсвует"

    await session.refresh(current_user)
    assert current_user.balance == before_deal_balance
