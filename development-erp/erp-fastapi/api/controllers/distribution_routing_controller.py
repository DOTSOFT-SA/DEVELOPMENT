"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from fastapi import APIRouter, Depends

from ..models.dto_models import ResponseWithUserID
from ..models.page_criteria_models import PageParams, VehicleDevelopmentCriteria, RouteDevelopmentCriteria, \
    LocationDevelopmentCriteria
from ..services.facades.distribution_routing_service_facade import DistributionRoutingServiceFacade
from ..services.location_development_service import LocationDevelopmentService
from ..services.route_development_service import RouteDevelopmentService
from ..services.vehicle_development_service import VehicleDevelopmentService
from ..utils.dependency_injection_container import (
    get_distribution_routing_facade,
    get_vehicle_development_service,
    get_route_development_service,
    get_location_development_service,
)
from ..utils.settings import settings

router = APIRouter()


@router.get("/distribution_routing_data", response_model=ResponseWithUserID)
async def get_distribution_routing_data(
        facade: DistributionRoutingServiceFacade = Depends(get_distribution_routing_facade)
) -> ResponseWithUserID:
    """
    Returns the JSON data model for distribution routing,
    assembled from location, route, and vehicle tables.

    @param facade: The DistributionRoutingServiceFacade dependency
    @return: The JSON data model with user_id included
    """
    data_model = await facade.build_data_model()
    return ResponseWithUserID(user_id=settings.CLIENT_DEVELOPMENT_USER_ID, data=data_model)


@router.get("/vehicle_development", response_model=ResponseWithUserID)
async def list_vehicle_development(
        page_params: PageParams = Depends(),
        criteria: VehicleDevelopmentCriteria = Depends(),
        service: VehicleDevelopmentService = Depends(get_vehicle_development_service),
) -> ResponseWithUserID:
    """
    Retrieve vehicle records with pagination and filtering.

    @param page_params: The query parameters for pagination.
    @param criteria: The query parameters for filtering (vehicle_id).
    @param service: The VehicleDevelopmentService for business logic and data access.
    @return: A list of VehicleDevelopment models with user_id included.
    """
    response = await service.get_all_vehicles(page_params, criteria)
    return ResponseWithUserID(user_id=settings.CLIENT_DEVELOPMENT_USER_ID, data=response)


@router.get("/route_development", response_model=ResponseWithUserID)
async def list_route_development(
        page_params: PageParams = Depends(),
        criteria: RouteDevelopmentCriteria = Depends(),
        service: RouteDevelopmentService = Depends(get_route_development_service),
) -> ResponseWithUserID:
    """
    Retrieve route records with pagination and filtering.

    @param page_params: The query parameters for pagination.
    @param criteria: The query parameters for filtering (route_id).
    @param service: The RouteDevelopmentService for business logic and data access.
    @return: A list of RouteDevelopment models with user_id included.
    """
    response = await service.get_all_routes(page_params, criteria)
    return ResponseWithUserID(user_id=settings.CLIENT_DEVELOPMENT_USER_ID, data=response)


@router.get("/location_development", response_model=ResponseWithUserID)
async def list_location_development(
        page_params: PageParams = Depends(),
        criteria: LocationDevelopmentCriteria = Depends(),
        service: LocationDevelopmentService = Depends(get_location_development_service),
) -> ResponseWithUserID:
    """
    Retrieve location records with pagination and filtering.

    @param page_params: The query parameters for pagination.
    @param criteria: The query parameters for filtering (location_id).
    @param service: The LocationDevelopmentService for business logic and data access.
    @return: A list of LocationDevelopment models with user_id included.
    """
    response = await service.get_all_locations(page_params, criteria)
    return ResponseWithUserID(user_id=settings.CLIENT_DEVELOPMENT_USER_ID, data=response)
