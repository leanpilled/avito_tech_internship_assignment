import pytest
import uuid
from data.db.models.deal import DealModel
from data.db.models.item import ItemModel
from data.db.models.transaction import TransactionModel
from data.db.models.user import UserModel
from passlib.context import CryptContext

from domain.entities.models import (
    CoinHistory,
    InfoResponse,
    Item,
    ReceivedCoin,
    SendCoin,
)


class TestVariables:
    USERNAME = "USERNAME"
    PASSWORD = "PASSWORD"
    BALANCE = 1000
    ITEM_TYPE = "ITEM_TYPE"
    ITEM_PRICE = 10
    INCOMING_TRANSACTION_AMOUNT = 5
    OUTGOING_TRANSACTION_AMOUNT = 5


@pytest.fixture
async def fill_user_info(session, current_user):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = UserModel(
        username=TestVariables.USERNAME,
        password=pwd_context.hash(TestVariables.PASSWORD),
        balance=TestVariables.BALANCE,
    )
    session.add(user)

    item = ItemModel(
        id=uuid.uuid4(),
        type=TestVariables.ITEM_TYPE,
        price=TestVariables.ITEM_PRICE,
    )
    session.add(item)
    await session.commit()

    incoming_transaction = TransactionModel(
        user_from_id=user.id,
        user_to_id=current_user.id,
        amount=TestVariables.INCOMING_TRANSACTION_AMOUNT,
    )
    session.add(incoming_transaction)

    outgoing_transaction = TransactionModel(
        user_from_id=current_user.id,
        user_to_id=user.id,
        amount=TestVariables.OUTGOING_TRANSACTION_AMOUNT,
    )
    session.add(outgoing_transaction)
    await session.commit()

    deal = DealModel(
        user_id=current_user.id,
        item_id=item.id,
    )
    session.add(deal)
    await session.commit()
    yield
    await session.delete(deal)
    await session.delete(item)
    await session.delete(incoming_transaction)
    await session.delete(outgoing_transaction)
    await session.delete(user)
    await session.commit()


async def test_get_info(client, fill_user_info, current_user):
    response = client.get("/info/")
    assert response.status_code == 200
    assert (
        response.json()
        == InfoResponse(
            coins=current_user.balance,
            inventory=[
                Item(
                    type=TestVariables.ITEM_TYPE,
                    quantity=1,
                ),
            ],
            coin_history=CoinHistory(
                received=[
                    ReceivedCoin(
                        from_user=TestVariables.USERNAME,
                        amount=TestVariables.INCOMING_TRANSACTION_AMOUNT,
                    ),
                ],
                send=[
                    SendCoin(
                        to_user=TestVariables.USERNAME,
                        amount=TestVariables.OUTGOING_TRANSACTION_AMOUNT,
                    ),
                ],
            ),
        ).model_dump()
    )
