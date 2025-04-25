"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from fastapi import APIRouter, Depends, Body

from ..models.dto_models import ResponseWithUserID, ListIdsDTO, ResponseSkuOrderDevelopmentWithUserID
from ..models.page_criteria_models import PageParams, SkuOrderDevelopmentCriteria
from ..services.sku_order_development_service import SkuOrderDevelopmentService
from ..utils.dependency_injection_container import get_sku_order_development_service
from ..utils.settings import settings

router = APIRouter()


@router.get("/sku_order_development", response_model=ResponseWithUserID)
async def list_sku_order_development(
        page_params: PageParams = Depends(),
        criteria: SkuOrderDevelopmentCriteria = Depends(),
        service: SkuOrderDevelopmentService = Depends(get_sku_order_development_service),
) -> ResponseWithUserID:
    """
    Retrieve SKU records from the 'sku_order_development' table with pagination and filtering.

    @param page_params: The query parameters for pagination.
    @param criteria: The query parameters for filtering.
    @param service: The SkuOrderDevelopmentService that contains business logic and data access.
    @return: A ResponseWithUserID model containing the user_id and the list of SkuOrderDevelopment models.
    """
    response = await service.get_all_skus(page_params, criteria)
    return ResponseWithUserID(user_id=settings.CLIENT_DEVELOPMENT_USER_ID, data=response)


@router.post("/sku_order_latest", response_model=ResponseSkuOrderDevelopmentWithUserID)
async def get_latest_sku_order(
        dto: ListIdsDTO = Body(...),
        service: SkuOrderDevelopmentService = Depends(get_sku_order_development_service)
) -> ResponseSkuOrderDevelopmentWithUserID:
    """
    Given a list of SkuOrderDevelopment IDs, returns the record with the LATEST order_date.

    @param dto: A DTO containing a list of IDs (dto.ids).
    @param service: The SkuOrderDevelopmentService for retrieving data.
    @return: A ResponseWithUserID model containing the user_id and either:
             - A single SkuOrderDevelopment record, or
             - An empty dict if none found.
    """
    record = await service.get_latest_sku_order_by_ids(dto.ids)

    # If record is None, you might return {} or None in the 'data' field
    return ResponseSkuOrderDevelopmentWithUserID(
        user_id=settings.CLIENT_DEVELOPMENT_USER_ID,
        data=record if record else {}
    )
