"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""
import asyncio

from sqlalchemy import text

from app.models import Base
from app.utils.database_connection import AsyncSessionLocal


async def insert_privileges(session):
    """
    Inserts predefined privileges into the 'privilege' table if they do not already exist.
    """
    privileges = [
        "ΔΙΑΧΕΙΡΙΣΤΗΣ",
        "ΠΡΟΒΛΕΨΗ ΖΗΤΗΣΗΣ",
        "ΣΥΝΙΣΤΩΜΕΝΗ ΠΟΣΟΤΗΤΑ ΑΠΟΘΕΜΑΤΩΝ",
        "ΔΡΟΜΟΛΟΓΗΣΗ",
    ]
    if privileges:
        await session.execute(text(
            "INSERT INTO privilege (name) VALUES " +
            ", ".join(f"('{p}')" for p in privileges)
        ))
        print("✅ Privileges inserted!")


async def main():
    async with AsyncSessionLocal() as session:
        async with session.begin():  # Begin transaction
            try:
                conn = await session.connection()
                # If `login_user` table exists, assuming that the other tables exists as well
                existing_tables = await conn.run_sync(
                    lambda c: c.dialect.has_table(c, "login_user")
                )
                if not existing_tables:
                    await conn.run_sync(Base.metadata.create_all)  # Create all tables from models.py
                    await insert_privileges(session)
                    print("✅ The tables were newly created!")
                else:
                    print("⚠️ Tables already exist. Skipping creation.")
            except Exception:
                raise  # Re-raise to trigger rollback


# if __name__ == '__main__':
#     asyncio.run(main())
