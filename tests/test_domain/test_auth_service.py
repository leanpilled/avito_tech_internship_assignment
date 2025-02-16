import unittest
from unittest.mock import AsyncMock, MagicMock
import uuid
from datetime import datetime, timezone
import jwt

from data.adapters.user_repo import UserRepo
from domain.entities.models import AuthResponse
from domain.exceptions import InvalidCredentials
from domain.services.auth_service import AuthService
from settings import settings


class TestAuthService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.settings = settings
        self.settings.TOKEN_LIVE_TIME = 30
        self.settings.SECRET_KEY = "test_secret"
        self.settings.ALGORITHM = "HS256"

        self.mock_user_repo = AsyncMock(spec=UserRepo)
        self.auth_service = AuthService(self.settings, self.mock_user_repo)
        self.user_id = uuid.uuid4()
        self.password = "test_password"
        self.wrong_password = "wrong_password"
        self.test_user = "test_user"

    def test_hash_password(self):
        hashed_password = self.auth_service._hash_password(self.password)
        self.assertTrue(
            self.auth_service._verify_password(self.password, hashed_password)
        )

    def test_verify_password(self):
        hashed_password = self.auth_service._hash_password(self.password)
        self.assertTrue(
            self.auth_service._verify_password(self.password, hashed_password)
        )
        self.assertFalse(
            self.auth_service._verify_password(self.wrong_password, hashed_password)
        )

    def test_generate_jwt(self):
        token = self.auth_service._generate_jwt(self.user_id)
        decoded = jwt.decode(
            token, self.settings.SECRET_KEY, algorithms=[self.settings.ALGORITHM]
        )
        self.assertEqual(decoded["user_id"], str(self.user_id))
        self.assertTrue(
            datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
            > datetime.now(timezone.utc)
        )

    async def test_login_user_existing_user(self):
        hashed_password = self.auth_service._hash_password(self.password)
        mock_user = MagicMock()
        mock_user.id = self.user_id
        mock_user.password = hashed_password
        self.mock_user_repo.get_user.return_value = mock_user

        response = await self.auth_service.login_user(self.test_user, self.password)

        self.mock_user_repo.get_user.assert_called_once_with(self.test_user)
        self.assertIsInstance(response, AuthResponse)
        self.assertTrue(
            jwt.decode(
                response.token,
                self.settings.SECRET_KEY,
                algorithms=[self.settings.ALGORITHM],
            )
        )

    async def test_login_user_create_new_user(self):
        new_user = MagicMock()
        new_user.id = self.user_id

        self.mock_user_repo.get_user.return_value = None
        self.mock_user_repo.create_user.return_value = new_user

        response = await self.auth_service.login_user(self.test_user, self.password)

        self.mock_user_repo.get_user.assert_called_once_with(self.test_user)
        self.mock_user_repo.create_user.assert_called_once()
        self.assertIsInstance(response, AuthResponse)
        self.assertTrue(
            jwt.decode(
                response.token,
                self.settings.SECRET_KEY,
                algorithms=[self.settings.ALGORITHM],
            )
        )

    async def test_login_user_invalid_password(self):
        mock_user = MagicMock()
        mock_user.id = self.user_id
        mock_user.password = self.auth_service._hash_password(self.password)
        self.mock_user_repo.get_user.return_value = mock_user

        with self.assertRaises(InvalidCredentials):
            await self.auth_service.login_user(self.test_user, self.wrong_password)

        self.mock_user_repo.get_user.assert_called_once_with(self.test_user)
