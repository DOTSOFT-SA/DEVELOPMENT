"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.orm_schema import UserErpApiORM


class UserErpApiRepository:
    """
    Repository to handle CRUD operations for the 'user_erp_api' table.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_user_erp_api_by_user_id(self, user_id: int):
        result = await self.session.execute(
            select(UserErpApiORM).where(UserErpApiORM.user_id == user_id)
        )
        return result.scalars().first()

    async def find_all_user_erp_api(self):
        """
        Retrieves all ERP API configurations from the database.
        @return: A list of UserErpApiORM objects.
        """
        result = await self.session.execute(select(UserErpApiORM))
        return result.scalars().all()
