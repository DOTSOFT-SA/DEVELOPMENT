"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from sqlalchemy.ext.asyncio import AsyncSession

from models.models import SkuMetric
from repositories.sku_metric_repository import SkuMetricRepository
from utils.database_connection import AsyncSessionLocal


async def add_sku_number_user_id_sku_order_record_id(
        session: AsyncSession, user_id: int, erp_sku_order_development_data: list
) -> None:
    """
    Add initial data for SKU metrics: sku_number, sku_order_record_id, and user_id.
    The rest fields will be None.

    @param session: An active AsyncSession instance for performing database operations.
    @param user_id: The unique identifier of the web app user to whom the data belongs.
    @param erp_sku_order_development_data: A list of dictionaries containing 'sku_number' and 'id' (sku_record_id).
    @return: None
    """
    try:
        sku_metric_repo = SkuMetricRepository(session)
        # We want to add only the records that do not exist in the DB already
        filtered_erp_sku_order_development_data = await sku_metric_repo.filter_erp_records_not_in_db(
            erp_sku_order_development_data, "sku_order_record_id")
        if not filtered_erp_sku_order_development_data:
            print("All given ERP SKU_ORDER records exist in the DB")
            return
        # Going through each record
        for record in filtered_erp_sku_order_development_data:
            sku_metric = SkuMetric(
                sku_number=record["sku_number"],
                sku_order_record_id=record["id"],  # Unique identifier from ERP sku_order_development data
                user_id=user_id,  # Associated user ID
            )
            # Create the record in the database
            await sku_metric_repo.create_sku_metric(sku_metric)
        print("sku_number, user_id, and sku_order_record_id added successfully in sku_metric.")
    except Exception as e:
        raise Exception(f"add_sku_number_user_id_sku_order_record_id(): {e}")


async def main(user_id: int, erp_sku_order_development_data: list):
    try:
        async with AsyncSessionLocal() as session:
            await add_sku_number_user_id_sku_order_record_id(
                session, user_id, erp_sku_order_development_data
            )
    except Exception as e:
        await session.rollback()
        raise e
