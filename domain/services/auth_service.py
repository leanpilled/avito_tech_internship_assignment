import uuid
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from data.adapters.user_repo import UserRepo
from domain.entities.models import AuthResponse
from domain.exceptions import InvalidCredentials
from settings import Settings


class AuthService:
    def __init__(
        self,
        settings: Settings,
        user_repo: UserRepo,
    ) -> None:
        self.token_live_time = settings.TOKEN_LIVE_TIME
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.user_repo = user_repo

    def _hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str):
        return self.pwd_context.verify(plain_password, hashed_password)

    def _generate_jwt(self, user_id: uuid.UUID) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=self.token_live_time)
        to_encode = {"user_id": str(user_id), "exp": expire}
        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return token

    async def login_user(self, username: str, password: str) -> AuthResponse:
        user = await self.user_repo.get_user(username)
        if not user:
            new_user = await self.user_repo.create_user(
                username=username,
                password=self._hash_password(password),
            )
            return AuthResponse(
                token=self._generate_jwt(new_user.id),
            )
        elif not self._verify_password(password, user.password):
            raise InvalidCredentials
        return AuthResponse(
            token=self._generate_jwt(user.id),
        )
