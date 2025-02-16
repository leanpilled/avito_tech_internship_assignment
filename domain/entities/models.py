from pydantic import BaseModel, Field
import uuid


class ReceivedCoin(BaseModel):
    from_user: str = Field(description="Имя пользователя, который отправил монеты.")
    amount: int = Field(description="Количество полученных монет.")


class SendCoin(BaseModel):
    to_user: str = Field(description="Имя пользователя, которому отправлены монеты.")
    amount: int = Field(description="Количество отправленных монет.")


class Item(BaseModel):
    type: str = Field(description="Тип предмета.")
    quantity: int = Field(description="Количество предметов.")


class ItemDto(BaseModel):
    id: uuid.UUID
    price: int
    type: str


class CoinHistory(BaseModel):
    received: list[ReceivedCoin | None]
    send: list[SendCoin | None]


class InfoResponse(BaseModel):
    coins: int = Field(description="Количество доступных монет.")
    inventory: list[Item | None]
    coin_history: CoinHistory


class AuthRequest(BaseModel):
    username: str = Field(description="Имя пользователя для аутентификации.")
    password: str = Field(description="Пароль для аутентификации.", format="password")


class AuthResponse(BaseModel):
    token: str = Field(description="JWT-токен для доступа к защищенным ресурсам.")


class SendCoinRequest(BaseModel):
    to_user: str = Field(
        description="Имя пользователя, которому нужно отправить монеты."
    )
    amount: int = Field(description="Количество монет, которые необходимо отправить.")


class ErrorResponse(BaseModel):
    errors: str = Field(description="Сообщение об ошибке, описывающее проблему.")
