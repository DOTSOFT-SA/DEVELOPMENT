"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import bcrypt

from ..models.models import User
from ..utils.settings import settings


class AuthRepository:
    @staticmethod
    async def get_user() -> User:
        """
        Retrieves a single user with a hashed password from the .env configuration.
        Repository that provides the single user (from .env) in a manner that
        mimics a "fetch from DB" but actually uses environment variables.

        @return: A User object containing the username and hashed password.
        """
        username = settings.API_USERNAME
        hashed_password = bcrypt.hashpw(
            settings.API_PASSWORD.encode("utf-8"),
            bcrypt.gensalt()  # Ensures users with identical passwords have unique hashes
        ).decode("utf-8")

        return User(username=username, password=hashed_password)
