"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from fastapi import APIRouter, Depends, Body

from ..models.dto_models import ResponseWithUserID, InventoryParamsDTO, ResponseInventoryParamsDevelopmentWithUserID
from ..models.page_criteria_models import PageParams, InventoryParamsCriteria
from ..services.inventory_params_development_service import InventoryParamsDevelopmentService
from ..utils.dependency_injection_container import get_inventory_params_development_service
from ..utils.settings import settings

router = APIRouter()


@router.get("/inventory_params_development", response_model=ResponseWithUserID)
async def list_inventory_params_development(
        page_params: PageParams = Depends(),
        criteria: InventoryParamsCriteria = Depends(),
        service: InventoryParamsDevelopmentService = Depends(get_inventory_params_development_service),
) -> ResponseWithUserID:
    """
    Retrieve inventory parameter records with pagination and filtering.

    @param page_params: The query parameters for pagination.
    @param criteria: The query parameters for filtering.
    @param service: The InventoryParamsDevelopmentService for business logic and data access.
    @return: A ResponseWithUserID model containing the user_id and inventory parameter records.
    """
    response = await service.get_all_inventory_params(page_params, criteria)
    return ResponseWithUserID(user_id=settings.CLIENT_DEVELOPMENT_USER_ID, data=response)


@router.post("/get_inventory_params_development_latest", response_model=ResponseInventoryParamsDevelopmentWithUserID)
async def get_latest_inventory_param_by_sku_number(
        inventory_dto: InventoryParamsDTO = Body(...),
        service: InventoryParamsDevelopmentService = Depends(get_inventory_params_development_service),
) -> ResponseInventoryParamsDevelopmentWithUserID:
    """
    Retrieve the latest inventory parameter record for a given SKU number based on 'created_at'.

    @param inventory_dto: The InventoryParamsDTO object containing the SKU number.
    @param service: The InventoryParamsDevelopmentService for business logic and data access.
    @return: A ResponseInventoryParamsDevelopmentWithUserID model containing the user_id and the latest InventoryParamsDevelopment record.
    """
    record = await service.get_latest_by_sku_number(inventory_dto.sku_number)
    return ResponseInventoryParamsDevelopmentWithUserID(user_id=settings.CLIENT_DEVELOPMENT_USER_ID,
                                                        data=record)
