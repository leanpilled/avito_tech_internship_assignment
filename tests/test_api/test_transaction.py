import pytest
from passlib.context import CryptContext
from sqlalchemy import and_, select

from data.db.models.transaction import TransactionModel
from data.db.models.user import UserModel
from domain.entities.models import SendCoinRequest
from tests.conftest import CurrentUser


class TestVariables:
    USERNAME = "USERNAME101111"
    NON_EXISTING_USERNAME = "NON_EXISTING_USERNAME"
    PASSWORD = "PASSWORD"
    BALANCE = 1000
    AVAILABLE_AMOUNT = 100
    UNAVAILABLE_AMOUNT = 10000
    NEGATIVE_AMOUNT = -100


@pytest.fixture
async def get_existing_user(session):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = UserModel(
        username=TestVariables.USERNAME,
        password=pwd_context.hash(TestVariables.PASSWORD),
        balance=TestVariables.BALANCE,
    )
    session.add(user)
    await session.commit()
    yield user
    await session.delete(user)
    await session.commit()


async def test_send_coin(client, session, current_user, get_existing_user):
    before_from_user_balance = current_user.balance
    before_to_user_balance = get_existing_user.balance

    response = client.post(
        "/sendCoin/",
        json=SendCoinRequest(
            to_user=TestVariables.USERNAME,
            amount=TestVariables.AVAILABLE_AMOUNT,
        ).model_dump(),
    )
    assert response.status_code == 200
    query = select(TransactionModel).where(
        and_(
            TransactionModel.user_from_id == current_user.id,
            TransactionModel.user_to_id == get_existing_user.id,
        )
    )
    result = await session.execute(query)
    transaction = result.scalar_one_or_none()
    assert transaction
    assert transaction.amount == TestVariables.AVAILABLE_AMOUNT
    await session.refresh(current_user)
    await session.refresh(get_existing_user)
    assert (
        before_from_user_balance
        == current_user.balance + TestVariables.AVAILABLE_AMOUNT
    )
    assert (
        before_to_user_balance
        == get_existing_user.balance - TestVariables.AVAILABLE_AMOUNT
    )

    await session.delete(transaction)
    await session.commit()


@pytest.mark.parametrize(
    "to_user, amount, status_code, error",
    [
        (
            TestVariables.USERNAME,
            TestVariables.UNAVAILABLE_AMOUNT,
            400,
            "Недостаточно средств",
        ),
        (
            TestVariables.NON_EXISTING_USERNAME,
            TestVariables.AVAILABLE_AMOUNT,
            422,
            "Такого пользователя не сущетсвует",
        ),
        (
            TestVariables.USERNAME,
            TestVariables.NEGATIVE_AMOUNT,
            422,
            "Сумма транзакции должна быть больше нуля",
        ),
        (
            CurrentUser.USERNAME,
            TestVariables.AVAILABLE_AMOUNT,
            403,
            "Невозможно отправить монетки этому пользователю",
        ),
    ],
)
async def test_send_coin_exceptions(
    client,
    session,
    current_user,
    get_existing_user,
    to_user,
    amount,
    status_code,
    error,
):
    before_from_user_balance = current_user.balance
    before_to_user_balance = get_existing_user.balance

    response = client.post(
        "/sendCoin/",
        json=SendCoinRequest(
            to_user=to_user,
            amount=amount,
        ).model_dump(),
    )
    assert response.status_code == status_code
    assert response.json()["errors"] == error
    query = select(TransactionModel).where(
        and_(
            TransactionModel.user_from_id == current_user.id,
            TransactionModel.user_to_id == get_existing_user.id,
        )
    )
    result = await session.execute(query)
    transaction = result.scalar_one_or_none()
    assert not transaction

    await session.refresh(current_user)
    await session.refresh(get_existing_user)
    assert before_from_user_balance == current_user.balance
    assert before_to_user_balance == get_existing_user.balance
