"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from ..models.models import User
from ..repositories.auth_repository import AuthRepository
from ..utils.settings import settings


class AuthService:

    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def authenticate_user(self, username: str, user_password: str) -> User | None:
        """
        Authenticates a user by verifying the provided credentials against the environment-based user.

        @param username: The username provided by the user attempting to authenticate.
        @param user_password: The plain text password provided by the user attempting to authenticate.
        @return: The authenticated User object if credentials are valid, or None if authentication fails.
        """
        env_user = await self.auth_repository.get_user()
        if env_user.username != username:
            return None
        if not self._verify_password(user_password, env_user.password):
            return None
        return env_user

    @staticmethod
    async def create_access_token(user_data: dict) -> str:
        """
        Create a JWT access token with an (new) expiration claim.

        @param user_data: A dictionary containing the user's data to include in the token payload.
        @return: A JWT access token as a string.
        """
        to_encode = user_data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def _verify_password(plain_password: str, password: str) -> bool:
        """
        Verifies if a plain text password matches the hashed password.

        @param plain_password: The plain text password to verify.
        @param password: The hashed password stored for the user.
        @return: True if the plain text password matches the hashed password, False otherwise.
        """
        return bcrypt.checkpw(plain_password.encode("utf-8"), password.encode("utf-8"))
