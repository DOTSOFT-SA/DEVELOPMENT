"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import List, Dict, Any

from sqlalchemy import update, select, and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import SkuMetric
from models.orm_schema import SkuMetricORM


class SkuMetricRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_sku_metric(self, sku_metric: SkuMetric):
        """
        Creates a new record in the `sku_metric` table.

        @param sku_metric: A pydantic SkuMetric object containing the data to create a record.
        """
        try:
            # Convert Pydantic model to SQLAlchemy ORM instance
            sku_metric_orm = SkuMetricORM(**sku_metric.dict())
            # Add and then commit the record to the session
            self.session.add(sku_metric_orm)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"create_sku_metric(): {e}")

    async def update_sku_metric_holidays_weekends_weather(self, sku_metric: SkuMetric):
        """
        Updates specific fields of a record in the `sku_metric` table.
        is_weekend, is_holiday, mean_temperature, rain

        @param sku_metric: A pydantic SkuMetric object containing the data to update a record.
        @raises NoResultFound: If no record with the given `sku_record_id` exists.
        """
        try:
            # Prepare the update operation
            result = await self.session.execute(
                update(SkuMetricORM)
                .where(SkuMetricORM.sku_order_record_id == sku_metric.sku_order_record_id)
                .values(
                    is_weekend=sku_metric.is_weekend,
                    is_holiday=sku_metric.is_holiday,
                    mean_temperature=sku_metric.mean_temperature,
                    rain=sku_metric.rain,
                )
                .execution_options(synchronize_session="fetch")
            )
            # Check if the record found before apply
            if result.rowcount == 0:
                raise NoResultFound(f"No record found with sku_record_id={sku_metric.sku_order_record_id}")
            # Apply
            await self.session.commit()
        except NoResultFound as e:
            raise NoResultFound(f"update_sku_metric(): {e}")
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"update_sku_metric(): {e}")

    async def update_sku_metric_trend_value(self, sku_metric: SkuMetric):
        """
        Updates the `trend_value` field of a record in the `sku_metric` table
        based on matching sku_order_record_id.

        @param sku_metric: A pydantic SkuMetric object containing the data to update a record.
        @raises NoResultFound: If no record with the given `sku_record_id` exists.
        """
        from sqlalchemy import update
        from sqlalchemy.exc import NoResultFound

        try:
            # We'll only update the trend_value column
            result = await self.session.execute(
                update(SkuMetricORM)
                .where(SkuMetricORM.sku_order_record_id == sku_metric.sku_order_record_id)
                .values(trend_value=sku_metric.trend_value)
                .execution_options(synchronize_session="fetch")
            )

            if result.rowcount == 0:
                raise NoResultFound(f"No record found with sku_record_id={sku_metric.sku_order_record_id}")
            await self.session.commit()

        except NoResultFound as e:
            raise NoResultFound(f"update_sku_metric_trend_value(): {e}")
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"update_sku_metric_trend_value(): {e}")

    async def update_sku_metric_average_competition_price_external(self, sku_metric: SkuMetric):
        """
        Updates the `average_competition_price_external` field of a record in the `sku_metric` table
        based on matching `sku_order_record_id`.

        @param sku_metric: A pydantic SkuMetric object containing the data to update a record.
        @raises NoResultFound: If no record with the given `sku_order_record_id` exists.
        """
        try:
            # Prepare the update operation
            result = await self.session.execute(
                update(SkuMetricORM)
                .where(SkuMetricORM.sku_order_record_id == sku_metric.sku_order_record_id)
                .values(
                    average_competition_price_external=sku_metric.average_competition_price_external
                )
                .execution_options(synchronize_session="fetch")
            )
            # Check if the record exists before applying the update
            if result.rowcount == 0:
                raise NoResultFound(f"No record found with sku_order_record_id={sku_metric.sku_order_record_id}")
            # Commit the transaction
            await self.session.commit()

        except NoResultFound as e:
            raise NoResultFound(f"update_sku_metric_web_scraping_values(): {e}")
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"update_sku_metric_web_scraping_values(): {e}")

    async def update_sku_metric_review_sentiment_score_and_timestamp(self, sku_metric: SkuMetric):
        """
        Updates only the `review_sentiment_score` and `review_sentiment_timestamp`
        fields of a record in the `sku_metric` table based on matching `sku_order_record_id`.

        @params sku_metric: SkuMetric
            A Pydantic model containing the review_sentiment_score, review_sentiment_timestamp,
            and sku_order_record_id to identify the record to update.
        @raises NoResultFound: If no record with the given `sku_order_record_id` exists.
        """
        try:
            result = await self.session.execute(
                update(SkuMetricORM)
                .where(SkuMetricORM.sku_order_record_id == sku_metric.sku_order_record_id)
                .values(
                    review_sentiment_score=sku_metric.review_sentiment_score,
                    review_sentiment_timestamp=sku_metric.review_sentiment_timestamp
                )
                .execution_options(synchronize_session="fetch")
            )

            if result.rowcount == 0:
                raise NoResultFound(
                    f"No record found with sku_order_record_id={sku_metric.sku_order_record_id}"
                )

            await self.session.commit()

        except NoResultFound as e:
            await self.session.rollback()
            raise NoResultFound(f"update_sku_metric_review_sentiment(): {e}")
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"update_sku_metric_review_sentiment(): {e}")

    async def filter_erp_records_not_in_db(
            self,
            erp_sku_order_development_data: List[Dict[str, Any]],
            db_column_name: str
    ) -> List[Dict[str, Any]]:
        """
        Returns only those records from 'erp_sku_order_development_data'
        that do NOT exist in the 'sku_metric' table based on the given 'db_column_name'.

        @param erp_sku_order_development_data: A list of dictionaries from the ERP system.
        @param db_column_name: The column in `sku_metric` to compare against (e.g., 'sku_order_record_id').
        @return: A list of dictionaries (ERP records) that are not present in the DB.
        """
        # Fetch all existing values of the given column from the database
        result = await self.session.execute(
            select(getattr(SkuMetricORM, db_column_name))
        )
        existing_ids = {row[0] for row in result.all()}
        # Compare each ERP record's 'id' against these existing IDs
        filtered_records = []
        for record in erp_sku_order_development_data:
            erp_id = record.get("id")  # ERP data's 'id' → db's sku_order_record_id
            if erp_id not in existing_ids:
                filtered_records.append(record)
        # Return
        return filtered_records

    async def filter_in_db_with_null_columns(
            self,
            erp_sku_order_development_data: List[Dict[str, Any]],
            db_null_column_names: List[str],
            db_identity_unique_col_name: str
    ) -> List[Dict[str, Any]]:
        """
        Returns only those ERP records that:
          1) Already exist in `sku_metric` (matched by `db_unique_col` == ERP record["id"]).
          2) Have ALL of the columns in `db_column_names` set to NULL in the DB.

        For example, if db_column_names = ["mean_temperature", "rain"],
        this method returns records in which both mean_temperature and rain are NULL in the DB.

        @param erp_sku_order_development_data: A list of dictionaries from ERP data, each having an "id" that maps to db_unique_col.
        @param db_null_column_names: The list of columns to check for NULL in the DB.
        @param db_identity_unique_col_name: The DB column that maps to the "id" field in the ERP records (default "sku_order_record_id").
        @return: A filtered list of dictionaries from ERP data that meet the above criteria.
        """
        # Build an AND condition: each column must be NULL
        null_conditions = []
        for col in db_null_column_names:
            col_attr = getattr(SkuMetricORM, col, None)
            if col_attr is None:
                # If the column doesn't exist in the ORM, skip or raise an error as needed
                raise ValueError(f"Column '{col}' does not exist in SkuMetricORM.")
            null_conditions.append(col_attr.is_(None))

        # We'll fetch all DB rows whose db_null_column_names are all NULL
        # (and we only need the unique column to match back to ERP data).
        stmt = select(getattr(SkuMetricORM, db_identity_unique_col_name)).where(and_(*null_conditions))
        result = await self.session.execute(stmt)
        existing_ids_with_nulls = {row[0] for row in result.fetchall()}

        # Filter the ERP records: keep only those whose 'id' is in existing_ids_with_nulls
        filtered_records = [
            record for record in erp_sku_order_development_data
            if record.get("id") in existing_ids_with_nulls
        ]

        return filtered_records
