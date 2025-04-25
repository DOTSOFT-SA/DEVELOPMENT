"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.orm_schema import LoginUserORM


class UserRepository:
    """
    Repository that handles CRUD operations for the 'login_user' table.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_user_exist_and_active_by_id(self, user_id: int) -> bool:
        """
        Checks if a user with the given ID exists in the database and is active.

        @param user_id: The ID of the user to check.
        @return: True if the user exists and active, False otherwise.
        """
        query = select(exists().where(LoginUserORM.id == user_id, LoginUserORM.is_active == True))
        result = await self.session.execute(query)
        return result.scalar()
