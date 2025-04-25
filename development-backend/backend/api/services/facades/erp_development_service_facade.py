"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import logging
from typing import List, Dict, Optional

import inject

from .erp_development_service_facade_interface import ErpDevelopmentServiceFacadeInterface
from ..sku_metric_service_interface import SkuMetricServiceInterface
from ...models.dtos.merged_sku_metric_dto import MergedSkuMetricDto
from ...repositories.erp_development_repository_interface import ErpDevelopmentRepositoryInterface
from ...services.user_erp_api_service_interface import UserErpApiServiceInterface
from ...utils.custom_exceptions import CustomLoggerException

logger = logging.getLogger(__name__)


class ErpDevelopmentServiceFacade(ErpDevelopmentServiceFacadeInterface):
    """
    A service that fetches external ERP data for a user,
    pulling configuration (URLs & credentials) from the UserErpApi DB record.
    """

    @inject.autoparams()
    def __init__(
            self,
            erp_development_repository: ErpDevelopmentRepositoryInterface,
            user_erp_api_service: UserErpApiServiceInterface,
            sku_metric_service: SkuMetricServiceInterface
    ):
        self.erp_development_repository = erp_development_repository
        self.user_erp_api_service = user_erp_api_service
        self.sku_metric_service = sku_metric_service

    def get_most_recent_sku_order_record(self, sku_order_record_ids: List[int], user_id: int) -> Dict | None:
        """
        Retrieves the most recent SKU order record from the external ERP system.

        :param sku_order_record_ids: List of record IDs to pass in the payload.
        :param user_id: The ID of the user who owns the ERP API config.
        :return: The 'data' portion from the ERP response (dict or None if no response).
        """
        # Make sure there's an ERP config in DB for that user
        user_erp_api = self.user_erp_api_service.get_user_erp_api(user_id)
        # Acquire token from that user's ERP API config
        token = self.erp_development_repository.fetch_erp_api_token(user_id)
        if not token:
            raise CustomLoggerException(f"Failed to retrieve ERP token for user_id={user_id}")
        # Build the URL & Send a POST request with {'ids': sku_order_record_ids} as JSON.
        url = user_erp_api.sku_order_latest_url
        payload = {"ids": sku_order_record_ids}
        logger.info(f"Sending POST to {url} with payload={payload}")
        json_resp = self.erp_development_repository.fetch_data_from_erp(url, token, method="POST", payload=payload)
        # The API response has {"user_id": X, "data": {...}}
        if not json_resp or "data" not in json_resp:
            logger.warning("No 'data' portion returned from ERP API for the latest SKU order record.")
            return None
        return json_resp["data"]

    def get_most_recent_inventory_params_record(self, sku_number: int, user_id: int) -> Dict | None:
        """
        Fetches the most recent inventory parameters record from the ERP system.
        The ERP API response includes {"user_id": <int>, "data": {...}}, but we only return the 'data' portion.

        :param sku_number: The SKU number to pass in the request.
        :param user_id: The ID of the user who owns the ERP API config.
        :return: dict: The 'data' portion of the API response (None if no response).
        """
        # Acquire the user's ERP config & token
        user_erp_api = self.user_erp_api_service.get_user_erp_api(user_id)
        token = self.erp_development_repository.fetch_erp_api_token(user_id)
        if not token:
            raise CustomLoggerException(f"Failed to retrieve ERP token for user_id={user_id}")
        # Send a POST request with {'sku_number': sku_number} as JSON.
        url = user_erp_api.inventory_params_latest_url
        payload = {"sku_number": sku_number}
        json_resp = self.erp_development_repository.fetch_data_from_erp(url, token, method="POST", payload=payload)
        # Return the 'data' portion or returns None
        if not json_resp or "data" not in json_resp:
            logger.warning("No 'data' portion returned from ERP API for the latest inventory params.")
            return None
        return json_resp["data"]

    def get_distribution_routing_data(self, user_id: int) -> Dict | None:
        """
        Fetch distribution routing data from the external ERP system for the given user.

        :param user_id: The ID of the user who owns the ERP API config.
        :return: The 'data' portion from the ERP response (dict) or None if no response.
        """
        # Acquire the user's ERP config & token
        user_erp_api = self.user_erp_api_service.get_user_erp_api(user_id)
        token = self.erp_development_repository.fetch_erp_api_token(user_id)
        if not token:
            raise CustomLoggerException(f"Failed to retrieve ERP token for user_id={user_id}")
        # GET the routing data
        url = user_erp_api.distribution_routing_url
        json_resp = self.erp_development_repository.fetch_data_from_erp(url, token, method="GET")
        # Return the 'data' portion or None if no response
        if not json_resp or "data" not in json_resp:
            logger.warning("No 'data' portion returned from ERP API for the distribution routing data.")
            return None
        return json_resp["data"]

    def get_merged_sku_metric_info(self, sku_number: int, user_id: int) -> Optional[MergedSkuMetricDto]:
        """
        Retrieves merged SKU metric information by combining:
        - Local SkuMetric data from the database.
        - External ERP data via external ERP API.

        Steps:
          1. Fetch all sku_order_record_ids for the given sku_number from the local database.
          2. Query the external ERP API to retrieve the most recent SKU order record.
          3A. Extract the 'id' field from the external ERP response.
          3B. Retrieve the corresponding local SkuMetric record using the extracted 'id'.
          4. Merge the relevant fields from the ERP data and SkuMetric object into a MergedSkuMetricDto.

        If any step fails due to missing data, the method returns None.

        :param sku_number: int: The SKU number for which we want the merged info.
        :param user_id: int: The user ID used to locate the matching client config for the ERP call.
        :return: MergedSkuMetricDto: A DTO containing combined local and external data, or None if no data is available.
        """
        # Step 1: Retrieve local record IDs
        record_ids = self.sku_metric_service.get_all_sku_order_record_ids_by_sku_number(sku_number)
        if not record_ids:
            logger.warning(f"No SkuMetric records found for sku_number={sku_number}.")
            return None
        # Step 2: ERP external call -> get only 'data' portion
        only_data = self.get_most_recent_sku_order_record(record_ids, user_id)
        if not only_data:
            logger.warning("No data returned from external ERP for these record IDs.")
            return None
        # Step 3A: Extract the 'id' from the ERP's 'data' portion
        external_record_id = only_data.get("id")
        if not external_record_id:
            logger.warning("No 'id' field in external ERP data.")
            return None
        # Step 3B: Find the local SkuMetric by this record_id
        sku_metric_obj = self.sku_metric_service.get_by_sku_order_record_id(external_record_id)
        if not sku_metric_obj:
            logger.warning(f"No local SkuMetric found for record_id={external_record_id}.")
            return None
        # Step 4: Merge relevant data into a MergedSkuMetricDto and return it
        return self._merge_data(only_data, sku_metric_obj)

    @staticmethod
    def _merge_data(only_data, sku_metric_obj) -> MergedSkuMetricDto:
        """
        Merges external ERP data and local SkuMetric data into a MergedSkuMetricDto.

        This method takes:
          1. `only_data` - A dictionary containing external ERP data related to an SKU order.
          2. `sku_metric_obj` - A local SkuMetric object retrieved from the database.

        It maps relevant fields from both sources to construct a `MergedSkuMetricDto`, ensuring that:
          - Date-related fields are taken from the ERP response.
          - Metrics such as `is_weekend`, `is_holiday`, and `review_sentiment_score` are sourced from the local database.

        :param only_data: Dict: The external ERP data dictionary.
        :param sku_metric_obj: SkuMetric: The local SkuMetric instance.
        :return: MergedSkuMetricDto: A DTO containing merged information from ERP and local data.
        """
        merged_dto = MergedSkuMetricDto(
            order_date=only_data.get("order_date"),
            sku_number=only_data.get("sku_number"),
            sku_name=only_data.get("sku_name"),
            class_display_name=only_data.get("class_display_name"),
            order_item_price_in_main_currency=only_data.get("order_item_price_in_main_currency"),
            order_item_unit_count=only_data.get("order_item_unit_count"),
            cl_price=only_data.get("cl_price"),
            is_weekend=sku_metric_obj.is_weekend,
            is_holiday=sku_metric_obj.is_holiday,
            mean_temperature=sku_metric_obj.mean_temperature,
            rain=sku_metric_obj.rain,
            average_competition_price_external=sku_metric_obj.average_competition_price_external,
            review_sentiment_score=sku_metric_obj.review_sentiment_score,
            review_sentiment_timestamp=sku_metric_obj.review_sentiment_timestamp,
            trend_value=sku_metric_obj.trend_value,
            sku_order_record_id=sku_metric_obj.sku_order_record_id
        )
        return merged_dto
