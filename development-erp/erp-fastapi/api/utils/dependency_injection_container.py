"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.auth_repository import AuthRepository
from ..repositories.inventory_params_development_repository import InventoryParamsDevelopmentRepository
from ..repositories.location_development_repository import LocationDevelopmentRepository
from ..repositories.route_development_repository import RouteDevelopmentRepository
from ..repositories.sku_order_development_repository import SkuOrderDevelopmentRepository
from ..repositories.vehicle_development_repository import VehicleDevelopmentRepository
from ..services.auth_service import AuthService
from ..services.facades.distribution_routing_service_facade import DistributionRoutingServiceFacade
from ..services.inventory_params_development_service import InventoryParamsDevelopmentService
from ..services.location_development_service import LocationDevelopmentService
from ..services.route_development_service import RouteDevelopmentService
from ..services.sku_order_development_service import SkuOrderDevelopmentService
from ..services.vehicle_development_service import VehicleDevelopmentService
from ..utils.database_session_manager import db_manager


# -----------------------
# AUTH DEPS
# -----------------------
async def get_auth_repository() -> AuthRepository:
    return AuthRepository()


async def get_auth_service(
        repo: AuthRepository = Depends(get_auth_repository)
) -> AuthService:
    return AuthService(repo)


# -----------------------
# DATABASE DEP FOR REPO
# -----------------------
async def get_db() -> AsyncSession:
    """
    This yields an AsyncSession from your DatabaseSessionManager
    so that each request has its own session context.
    """
    async with db_manager.get_db() as session:
        yield session


# -----------------------
# SKU_ORDER_DEVELOPMENT DEPS
# -----------------------
def get_sku_order_development_repo(
        session: AsyncSession = Depends(get_db)  # <-- Inject the session here
) -> SkuOrderDevelopmentRepository:
    return SkuOrderDevelopmentRepository(session)


def get_sku_order_development_service(
        repo: SkuOrderDevelopmentRepository = Depends(get_sku_order_development_repo)
) -> SkuOrderDevelopmentService:
    return SkuOrderDevelopmentService(repo)


# -----------------------
# INVENTORY_PARAMS_DEVELOPMENT DEPS
# -----------------------
def get_inventory_params_development_repo(
        session: AsyncSession = Depends(get_db)
) -> InventoryParamsDevelopmentRepository:
    return InventoryParamsDevelopmentRepository(session)


def get_inventory_params_development_service(
        repo: InventoryParamsDevelopmentRepository = Depends(get_inventory_params_development_repo)
) -> InventoryParamsDevelopmentService:
    return InventoryParamsDevelopmentService(repo)


# -----------------------
# VEHICLE_DEVELOPMENT DEPS
# -----------------------
def get_vehicle_development_repo(
        session: AsyncSession = Depends(get_db)
) -> VehicleDevelopmentRepository:
    return VehicleDevelopmentRepository(session)


def get_vehicle_development_service(
        repo: VehicleDevelopmentRepository = Depends(get_vehicle_development_repo)
) -> VehicleDevelopmentService:
    return VehicleDevelopmentService(repo)


# -----------------------
# LOCATION_DEVELOPMENT DEPS
# -----------------------
def get_location_development_repo(
        session: AsyncSession = Depends(get_db)
) -> LocationDevelopmentRepository:
    return LocationDevelopmentRepository(session)


def get_location_development_service(
        repo: LocationDevelopmentRepository = Depends(get_location_development_repo)
) -> LocationDevelopmentService:
    return LocationDevelopmentService(repo)


# -----------------------
# ROUTE_DEVELOPMENT DEPS
# -----------------------
def get_route_development_repo(
        session: AsyncSession = Depends(get_db)
) -> RouteDevelopmentRepository:
    return RouteDevelopmentRepository(session)


def get_route_development_service(
        repo: RouteDevelopmentRepository = Depends(get_route_development_repo)
) -> RouteDevelopmentService:
    return RouteDevelopmentService(repo)


def get_distribution_routing_facade(
        location_service: LocationDevelopmentService = Depends(get_location_development_service),
        route_service: RouteDevelopmentService = Depends(get_route_development_service),
        vehicle_service: VehicleDevelopmentService = Depends(get_vehicle_development_service),
) -> DistributionRoutingServiceFacade:
    return DistributionRoutingServiceFacade(
        location_service=location_service,
        route_service=route_service,
        vehicle_service=vehicle_service
    )
