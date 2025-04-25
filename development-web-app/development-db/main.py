"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import asyncio

from app.services import create_tables, add_users_service


async def main():
    try:
        await create_tables.main()  # Create tables
        await add_users_service.main()  # Register users
        print("✅ All actions attempted!")
    except Exception as e:
        print(f"❌ {e}")


if __name__ == '__main__':
    asyncio.run(main())
