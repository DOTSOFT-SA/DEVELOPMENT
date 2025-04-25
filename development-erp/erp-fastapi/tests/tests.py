"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import os
import sys
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from factory import Factory, Faker

from api.models.page_criteria_models import SkuOrderDevelopmentCriteria, PageParams, InventoryParamsCriteria, \
    VehicleDevelopmentCriteria, LocationDevelopmentCriteria, RouteDevelopmentCriteria
from api.repositories.inventory_params_development_repository import InventoryParamsDevelopmentRepository
from api.repositories.location_development_repository import LocationDevelopmentRepository
from api.repositories.route_development_repository import RouteDevelopmentRepository
from api.repositories.vehicle_development_repository import VehicleDevelopmentRepository
from api.services.inventory_params_development_service import InventoryParamsDevelopmentService
from api.services.location_development_service import LocationDevelopmentService
from api.services.route_development_service import RouteDevelopmentService
from api.services.vehicle_development_service import VehicleDevelopmentService

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import your models & services
from api.models.models import SkuOrderDevelopment, InventoryParamsDevelopment, VehicleDevelopment, LocationDevelopment, \
    RouteDevelopment
from api.services.sku_order_development_service import SkuOrderDevelopmentService
from api.repositories.sku_order_development_repository import SkuOrderDevelopmentRepository


# -------------- FACTORY SETUP -------------- #
class SkuOrderDevelopmentFactory(Factory):
    """Factory to create mock SkuOrderDevelopment objects."""

    class Meta:
        model = SkuOrderDevelopment

    id = Faker('random_int', min=1, max=9999)
    sku_number = Faker('random_int', min=1, max=999999)
    sku_name = Faker('word')
    review_count = Faker('pyfloat', positive=True)
    review_score = Faker('pyfloat', positive=True)
    class_display_name = Faker('word')
    sku_short_description = Faker('sentence')
    order_item_price_in_main_currency = Faker('pyfloat', positive=True)
    order_item_unit_count = Faker('random_int', min=1, max=1000)
    order_date = Faker('date_time_this_year')
    product_cost = Faker('pyfloat', positive=True)
    cl_price = Faker('pyfloat', positive=True)
    price_date = Faker('date_object')


class InventoryParamsDevelopmentFactory(Factory):
    """Factory to create mock InventoryParamsDevelopment objects."""

    class Meta:
        model = InventoryParamsDevelopment

    id = Faker('random_int', min=1, max=9999)
    sku_number = Faker('random_int', min=1, max=999999)
    stock_level = Faker('random_int', min=1, max=1000)
    time_period_t = Faker('pyfloat', positive=True)
    fixed_order_cost_k = Faker('pyfloat', positive=True)
    unit_cost_c = Faker('pyfloat', positive=True)
    penalty_cost_p = Faker('pyfloat', positive=True)
    holding_cost_rate_i = Faker('pyfloat', positive=True)
    truckload_capacity_ftl = Faker('pyfloat', positive=True)
    transportation_cost_tr = Faker('pyfloat', positive=True)
    created_at = Faker('date_time_this_year')


class VehicleDevelopmentFactory(Factory):
    """Factory to create mock VehicleDevelopment objects."""

    class Meta:
        model = VehicleDevelopment

    id = Faker('random_int', min=1, max=9999)
    vehicle_id = Faker('random_int', min=1, max=9999)
    capacity = Faker('random_int', min=1, max=500)
    cost_per_trip = Faker('pyfloat', positive=True)
    created_at = Faker('date_time_this_year')


class LocationDevelopmentFactory(Factory):
    """Factory to create mock LocationDevelopment objects."""

    class Meta:
        model = LocationDevelopment

    id = Faker('random_int', min=1, max=9999)
    location_id = Faker('random_int', min=1, max=9999)
    location_name = Faker("word")
    demand = Faker('random_int', min=1, max=500)
    is_depot = Faker('boolean')
    created_at = Faker('date_time_this_year')


class RouteDevelopmentFactory(Factory):
    """Factory to create mock RouteDevelopment objects."""

    class Meta:
        model = RouteDevelopment

    id = Faker('random_int', min=1, max=9999)
    route_id = Faker('random_int', min=1, max=9999)
    distance = Faker('pyfloat', positive=True)
    traffic_factor = Faker('pyfloat', positive=True)
    source_location_id = Faker('random_int', min=1, max=9999)
    destination_location_id = Faker('random_int', min=1, max=9999)
    created_at = Faker('date_time_this_year')


# -------------- CONFIGURATIONS -------------- #
@pytest_asyncio.fixture
async def mock_repository():
    """
    Pytest fixture to create a mock SkuOrderDevelopmentRepository.
    We use AsyncMock because repository methods are async.
    """
    repo = AsyncMock()
    return repo


@pytest_asyncio.fixture
async def sku_service(mock_repository):
    """
    Returns an instance of SkuOrderDevelopmentService
    with a mocked repository.
    """
    mock_repo: SkuOrderDevelopmentRepository = mock_repository
    return SkuOrderDevelopmentService(mock_repo)


@pytest_asyncio.fixture
async def inventory_service(mock_repository):
    """
    Returns an instance of InventoryParamsDevelopmentService
    with a mocked repository.
    """
    mock_repo: InventoryParamsDevelopmentRepository = mock_repository
    return InventoryParamsDevelopmentService(mock_repo)


@pytest_asyncio.fixture
async def vehicle_service(mock_repository):
    """
    Returns an instance of VehicleDevelopmentService
    with a mocked repository.
    """
    mock_repo: VehicleDevelopmentRepository = mock_repository
    return VehicleDevelopmentService(mock_repo)


@pytest_asyncio.fixture
async def location_service(mock_repository):
    """
    Returns an instance of LocationDevelopmentService
    with a mocked repository.
    """
    mock_repo: LocationDevelopmentRepository = mock_repository
    return LocationDevelopmentService(mock_repo)


@pytest_asyncio.fixture
async def route_service(mock_repository):
    """
    Returns an instance of RouteDevelopmentService
    with a mocked repository.
    """
    mock_repo: RouteDevelopmentRepository = mock_repository
    return RouteDevelopmentService(mock_repo)


# -------------- TESTS - SKU_ORDER_DEVELOPMENT_SERVICE -------------- #

@pytest.mark.asyncio
async def test_get_all_skus_empty(sku_service, mock_repository):
    """
    Test when the repository returns an empty list of SKUs.
    """
    # Given
    mock_repository.fetch_all_skus.return_value = []
    # When
    page_params = PageParams(page=1, page_size=10)
    criteria = SkuOrderDevelopmentCriteria()
    # Then
    skus = await sku_service.get_all_skus(page_params, criteria)
    assert skus == []
    # Make sure the repository call was awaited with the correct parameters
    mock_repository.fetch_all_skus.assert_awaited_once_with(page_params, criteria)


@pytest.mark.asyncio
async def test_get_all_skus_non_empty(sku_service, mock_repository):
    """
    Test when the repository returns multiple SKUs.
    """
    # Given - Generate a list of random SkuOrderDevelopment objects
    fake_skus = SkuOrderDevelopmentFactory.build_batch(5)
    mock_repository.fetch_all_skus.return_value = fake_skus
    # When
    page_params = PageParams(page=1, page_size=10)
    criteria = SkuOrderDevelopmentCriteria(sku_number=123)
    # Then
    skus = await sku_service.get_all_skus(page_params, criteria)
    assert len(skus) == 5
    # Check that they are actually the factory objects
    for sku in skus:
        assert isinstance(sku, SkuOrderDevelopment)
    # Make sure the repository call was awaited with the correct parameters
    mock_repository.fetch_all_skus.assert_awaited_once_with(page_params, criteria)


@pytest.mark.asyncio
async def test_get_all_skus_filter_by_name(sku_service, mock_repository):
    """
    Test filtering by sku_name or other fields.
    """
    # Given
    fake_skus = [
        # Create multiple SKUs, one matches the name "Widget"
        SkuOrderDevelopmentFactory(sku_name="Widget"),
        *SkuOrderDevelopmentFactory.build_batch(3)
    ]
    mock_repository.fetch_all_skus.return_value = fake_skus
    # When
    page_params = PageParams(page=1, page_size=10)
    criteria = SkuOrderDevelopmentCriteria(sku_name="Widget")
    # Then
    skus = await sku_service.get_all_skus(page_params, criteria)
    assert len(skus) == 4
    assert skus[0].sku_name == "Widget"  # The first item has to be ' sku_name == "Widget" '
    mock_repository.fetch_all_skus.assert_awaited_once_with(page_params, criteria)  # Confirm the repo call


@pytest.mark.asyncio
async def test_get_latest_sku_order_by_ids_no_ids(sku_service, mock_repository):
    """
    Test when the list of IDs is empty -> should return None (or possibly an empty dict).
    """
    # Given
    mock_repository.fetch_latest_sku_order_by_ids.return_value = None
    # When
    result = await sku_service.get_latest_sku_order_by_ids([])
    # Then
    assert result is None
    # Also ensure the repository method wasn't even called with an empty list or it returned quickly
    mock_repository.fetch_latest_sku_order_by_ids.assert_awaited_once_with([])


@pytest.mark.asyncio
async def test_get_latest_sku_order_by_ids_found(sku_service, mock_repository):
    """
    Test that we get a single record with the max order_date among the given IDs.
    """
    # Given
    fake_record = SkuOrderDevelopmentFactory()
    mock_repository.fetch_latest_sku_order_by_ids.return_value = fake_record
    # When
    ids_list = [10, 20, 45]
    result = await sku_service.get_latest_sku_order_by_ids(ids_list)
    # Then
    assert result == fake_record
    mock_repository.fetch_latest_sku_order_by_ids.assert_awaited_once_with(ids_list)


@pytest.mark.asyncio
async def test_get_latest_sku_order_by_ids_not_found(sku_service, mock_repository):
    """
    Test that if no matching records are found, we get None back.
    """
    # Given
    mock_repository.fetch_latest_sku_order_by_ids.return_value = None
    # When
    ids_list = [999, 1000]
    result = await sku_service.get_latest_sku_order_by_ids(ids_list)
    # Then
    assert result is None
    mock_repository.fetch_latest_sku_order_by_ids.assert_awaited_once_with(ids_list)


# -------------- TESTS - INVENTORY_PARAMS_DEVELOPMENT_SERVICE -------------- #
@pytest.mark.asyncio
async def test_get_all_inventory_params_empty(inventory_service, mock_repository):
    """
    Test when the repository returns an empty list of inventory parameters.
    """
    # Given
    mock_repository.fetch_all_inventory_params.return_value = []
    # When
    page_params = PageParams(page=1, page_size=10)
    criteria = InventoryParamsCriteria()
    # Then
    inventory_params = await inventory_service.get_all_inventory_params(page_params, criteria)
    assert inventory_params == []
    mock_repository.fetch_all_inventory_params.assert_awaited_once_with(page_params, criteria)


@pytest.mark.asyncio
async def test_get_all_inventory_params_non_empty(inventory_service, mock_repository):
    """
    Test when the repository returns multiple inventory parameter records.
    """
    # Given - Generate a list of random InventoryParamsDevelopment objects
    fake_inventory_params = InventoryParamsDevelopmentFactory.build_batch(5)
    mock_repository.fetch_all_inventory_params.return_value = fake_inventory_params
    # When
    page_params = PageParams(page=1, page_size=10)
    criteria = InventoryParamsCriteria(sku_number=123)
    # Then
    inventory_params = await inventory_service.get_all_inventory_params(page_params, criteria)
    assert len(inventory_params) == 5
    for param in inventory_params:
        assert isinstance(param, InventoryParamsDevelopment)
    mock_repository.fetch_all_inventory_params.assert_awaited_once_with(page_params, criteria)


@pytest.mark.asyncio
async def test_get_all_inventory_params_filter_by_sku_number(inventory_service, mock_repository):
    """
    Test filtering by sku_number.
    """
    # Given
    fake_inventory_params = [
        InventoryParamsDevelopmentFactory(sku_number=12345),
        *InventoryParamsDevelopmentFactory.build_batch(3)
    ]
    mock_repository.fetch_all_inventory_params.return_value = fake_inventory_params
    # When
    page_params = PageParams(page=1, page_size=10)
    criteria = InventoryParamsCriteria(sku_number=12345)
    # Then
    inventory_params = await inventory_service.get_all_inventory_params(page_params, criteria)
    assert len(inventory_params) == 4
    assert inventory_params[0].sku_number == 12345
    mock_repository.fetch_all_inventory_params.assert_awaited_once_with(page_params, criteria)


# -------------- TESTS - VEHICLE_DEVELOPMENT_SERVICE -------------- #

@pytest.mark.asyncio
async def test_get_all_vehicles_empty(vehicle_service, mock_repository):
    """
    Test when the repository returns an empty list of vehicles.
    """
    # Given
    mock_repository.fetch_all_vehicles.return_value = []
    # When
    page_params = PageParams(page=1, page_size=10)
    criteria = VehicleDevelopmentCriteria()
    # Then
    vehicles = await vehicle_service.get_all_vehicles(page_params, criteria)
    assert vehicles == []
    mock_repository.fetch_all_vehicles.assert_awaited_once_with(page_params, criteria)


@pytest.mark.asyncio
async def test_get_all_vehicles_non_empty(vehicle_service, mock_repository):
    """
    Test when the repository returns multiple vehicle records.
    """
    # Given - Generate a list of random VehicleDevelopment objects
    fake_vehicles = VehicleDevelopmentFactory.build_batch(5)
    mock_repository.fetch_all_vehicles.return_value = fake_vehicles
    # When
    page_params = PageParams(page=1, page_size=10)
    criteria = VehicleDevelopmentCriteria(vehicle_id=123)
    # Then
    vehicles = await vehicle_service.get_all_vehicles(page_params, criteria)
    assert len(vehicles) == 5
    for vehicle in vehicles:
        assert isinstance(vehicle, VehicleDevelopment)
    mock_repository.fetch_all_vehicles.assert_awaited_once_with(page_params, criteria)


@pytest.mark.asyncio
async def test_get_all_vehicles_filter_by_vehicle_id(vehicle_service, mock_repository):
    """
    Test filtering by vehicle_id.
    """
    # Given
    fake_vehicles = [
        VehicleDevelopmentFactory(vehicle_id=12345),
        *VehicleDevelopmentFactory.build_batch(3)
    ]
    mock_repository.fetch_all_vehicles.return_value = fake_vehicles
    # When
    page_params = PageParams(page=1, page_size=10)
    criteria = VehicleDevelopmentCriteria(vehicle_id=12345)
    # Then
    vehicles = await vehicle_service.get_all_vehicles(page_params, criteria)
    assert len(vehicles) == 4
    assert vehicles[0].vehicle_id == 12345
    mock_repository.fetch_all_vehicles.assert_awaited_once_with(page_params, criteria)


@pytest.mark.asyncio
async def test_get_latest_by_sku_number_found(inventory_service, mock_repository):
    """
    Test retrieving the latest inventory parameter record for a given SKU number.
    """
    # Given
    sku_number = 12345
    fake_record = InventoryParamsDevelopmentFactory(sku_number=sku_number)
    mock_repository.fetch_latest_by_sku_number.return_value = fake_record

    # When
    result = await inventory_service.get_latest_by_sku_number(sku_number)

    # Then
    assert result == fake_record
    mock_repository.fetch_latest_by_sku_number.assert_awaited_once_with(sku_number)


@pytest.mark.asyncio
async def test_get_latest_by_sku_number_not_found(inventory_service, mock_repository):
    """
    Test when no inventory parameter record is found for a given SKU number.
    """
    # Given
    sku_number = 99999
    mock_repository.fetch_latest_by_sku_number.return_value = None

    # When
    result = await inventory_service.get_latest_by_sku_number(sku_number)

    # Then
    assert result is None
    mock_repository.fetch_latest_by_sku_number.assert_awaited_once_with(sku_number)


# -------------- TESTS - LOCATION_DEVELOPMENT_SERVICE -------------- #

@pytest.mark.asyncio
async def test_get_all_locations_empty(location_service, mock_repository):
    """
    Test when the repository returns an empty list of locations.
    """
    # Given
    mock_repository.fetch_all_locations.return_value = []
    # When
    page_params = PageParams(page=1, page_size=10)
    criteria = LocationDevelopmentCriteria()
    # Then
    locations = await location_service.get_all_locations(page_params, criteria)
    assert locations == []
    mock_repository.fetch_all_locations.assert_awaited_once_with(page_params, criteria)


@pytest.mark.asyncio
async def test_get_all_locations_non_empty(location_service, mock_repository):
    """
    Test when the repository returns multiple location records.
    """
    # Given - Generate a list of random LocationDevelopment objects
    fake_locations = LocationDevelopmentFactory.build_batch(5)
    mock_repository.fetch_all_locations.return_value = fake_locations
    # When
    page_params = PageParams(page=1, page_size=10)
    criteria = LocationDevelopmentCriteria(location_id=123)
    # Then
    locations = await location_service.get_all_locations(page_params, criteria)
    assert len(locations) == 5
    for location in locations:
        assert isinstance(location, LocationDevelopment)
    mock_repository.fetch_all_locations.assert_awaited_once_with(page_params, criteria)


@pytest.mark.asyncio
async def test_get_all_locations_filter_by_location_id(location_service, mock_repository):
    """
    Test filtering by location_id.
    """
    # Given
    fake_locations = [
        LocationDevelopmentFactory(location_id=12345),
        *LocationDevelopmentFactory.build_batch(3)
    ]
    mock_repository.fetch_all_locations.return_value = fake_locations
    # When
    page_params = PageParams(page=1, page_size=10)
    criteria = LocationDevelopmentCriteria(location_id=12345)
    # Then
    locations = await location_service.get_all_locations(page_params, criteria)
    assert len(locations) == 4
    assert locations[0].location_id == 12345
    mock_repository.fetch_all_locations.assert_awaited_once_with(page_params, criteria)


# -------------- TESTS - ROUTE_DEVELOPMENT_SERVICE -------------- #

@pytest.mark.asyncio
async def test_get_all_routes_empty(route_service, mock_repository):
    """
    Test when the repository returns an empty list of routes.
    """
    # Given
    mock_repository.fetch_all_routes.return_value = []
    # When
    page_params = PageParams(page=1, page_size=10)
    criteria = RouteDevelopmentCriteria()
    # Then
    routes = await route_service.get_all_routes(page_params, criteria)
    assert routes == []
    mock_repository.fetch_all_routes.assert_awaited_once_with(page_params, criteria)


@pytest.mark.asyncio
async def test_get_all_routes_non_empty(route_service, mock_repository):
    """
    Test when the repository returns multiple route records.
    """
    # Given - Generate a list of random RouteDevelopment objects
    fake_routes = RouteDevelopmentFactory.build_batch(5)
    mock_repository.fetch_all_routes.return_value = fake_routes
    # When
    page_params = PageParams(page=1, page_size=10)
    criteria = RouteDevelopmentCriteria(route_id=123)
    # Then
    routes = await route_service.get_all_routes(page_params, criteria)
    assert len(routes) == 5
    for route in routes:
        assert isinstance(route, RouteDevelopment)
    mock_repository.fetch_all_routes.assert_awaited_once_with(page_params, criteria)


@pytest.mark.asyncio
async def test_get_all_routes_filter_by_route_id(route_service, mock_repository):
    """
    Test filtering by route_id.
    """
    # Given
    fake_routes = [
        RouteDevelopmentFactory(route_id=12345),
        *RouteDevelopmentFactory.build_batch(3)
    ]
    mock_repository.fetch_all_routes.return_value = fake_routes
    # When
    page_params = PageParams(page=1, page_size=10)
    criteria = RouteDevelopmentCriteria(route_id=12345)
    # Then
    routes = await route_service.get_all_routes(page_params, criteria)
    assert len(routes) == 4
    assert routes[0].route_id == 12345
    mock_repository.fetch_all_routes.assert_awaited_once_with(page_params, criteria)


@pytest.mark.asyncio
async def test_get_all_routes_filter_by_source_and_destination(route_service, mock_repository):
    """
    Test filtering by source_location_id and destination_location_id.
    """
    # Given
    fake_routes = [
        RouteDevelopmentFactory(source_location_id=1, destination_location_id=2),
        *RouteDevelopmentFactory.build_batch(3)
    ]
    mock_repository.fetch_all_routes.return_value = fake_routes
    # When
    page_params = PageParams(page=1, page_size=10)
    criteria = RouteDevelopmentCriteria(source_location_id=1, destination_location_id=2)
    # Then
    routes = await route_service.get_all_routes(page_params, criteria)
    assert len(routes) == 4
    assert routes[0].source_location_id == 1
    assert routes[0].destination_location_id == 2
    mock_repository.fetch_all_routes.assert_awaited_once_with(page_params, criteria)
