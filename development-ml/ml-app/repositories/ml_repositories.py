"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import SkuMetric, \
    MlModel
from models.orm_schema import SkuMetricORM, MlModelORM


class SkuMetricRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_sku_metrics_by_user_id(self, user_id: int) -> List[SkuMetric]:
        """
        Retrieves all SkuMetric records for the specified user_id.

        @param user_id: The user ID to filter SkuMetric records.
        @return: A list of SkuMetric objects corresponding to the user_id.
        """
        try:
            # Query to fetch all SkuMetric records matching the given user_id
            result = await self.session.execute(
                select(SkuMetricORM).where(SkuMetricORM.user_id == user_id)
            )
            sku_metric_records = result.scalars().all()

            # Convert ORM objects to Pydantic models
            return [SkuMetric.from_orm(record) for record in sku_metric_records]

        except Exception as e:
            raise Exception(f"get_all_sku_metrics_by_user_id(): {e}")


class MlModelRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_or_update_ml_model(self, ml_model: MlModel):
        """
        Creates a new ML model record if it doesn't exist,
        or updates the 'model_file' if it does.

        @param ml_model: A pydantic MlModel object containing the binary file and metadata.
        """
        try:
            # Check if record exists for this user_id + model_type
            result = await self.session.execute(
                select(MlModelORM).where(
                    MlModelORM.user_id == ml_model.user_id,
                    MlModelORM.model_type == ml_model.model_type
                )
            )
            existing_record = result.scalars().first()
            if existing_record:
                # Modify the model_file to trigger an update
                existing_record.model_file = ml_model.model_file
                # Add it back to the session to ensure update is detected
                self.session.add(existing_record)
            else:
                # Create a new record
                new_record = MlModelORM(**ml_model.dict())
                self.session.add(new_record)
            # Commit changes
            await self.session.commit()
        except Exception as exc:
            await self.session.rollback()
            raise exc
