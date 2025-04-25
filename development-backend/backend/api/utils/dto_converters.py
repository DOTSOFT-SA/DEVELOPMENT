"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import datetime

import inject

from ..models.dtos.inventory_service_dto import InventoryOptimizationDto
from ..models.dtos.user_dto import RegisterUserDto, UserDto
from ..models.inventory_optimization import InventoryOptimization
from ..models.login_user import LoginUser
from ..services.facades.erp_development_service_facade import ErpDevelopmentServiceFacadeInterface
from ..services.sku_metric_service import SkuMetricServiceInterface

"""
This is a helper file that includes all the functions for converting Data Transfer Objects (DTOs) 
into Django model instances. It keeps the code organized and easy to reuse across the application.
"""


def register_user_dto_to_login_user(user_dto: RegisterUserDto, new_updated_at: datetime.datetime = None) -> LoginUser:
    """
    Convert a RegisterUserDto instance into a LoginUser model instance.
    This function takes a RegisterUserDto, which acts as a data transfer object,
    and maps its fields to create a LoginUser model instance.
    The 'updated_at' timestamp is optional and defaults to None.

    @param user_dto: RegisterUserDto - A Data Transfer Object containing user input data (email, password, role).
    @param new_updated_at: datetime.datetime (optional) - The timestamp for the 'updated_at' field. Defaults to None.
    @return: LoginUser - A new instance of the LoginUser model with mapped fields.
    """
    return LoginUser(
        email=user_dto.email,
        password=user_dto.password,
        role=user_dto.role,
        updated_at=new_updated_at
    )


def user_dto_to_login_user(user_dto: UserDto) -> LoginUser:
    """
    Convert a UserDto instance into a LoginUser model instance.
    This function maps the fields from the UserDto to a new or existing LoginUser model instance.

    @param user_dto: UserDto
        A Data Transfer Object containing user data
        (id, email, role, is_active, updated_at, created_at, login_at, privilege_names).
    @return: LoginUser
        A new or updated instance of the LoginUser model with mapped fields.
    """
    return LoginUser(
        id=user_dto.id,
        email=user_dto.email,
        role=user_dto.role,
        is_active=user_dto.is_active,
        updated_at=user_dto.updated_at,
        created_at=user_dto.created_at,
        login_at=user_dto.login_at,
    )


def login_user_to_user_dto(login_user: LoginUser, privilege_names: list = None) -> UserDto:
    """
    Convert a LoginUser model instance into a UserDto instance.
    This function maps the fields from the LoginUser model to a new UserDto instance.

    @param login_user: LoginUser
        A Django model instance containing user data (id, email, role, is_active, updated_at, created_at, login_at).
    @param privilege_names: list (optional)
        A list of privilege names associated with the user.
    @return: UserDto
        A new instance of UserDto with mapped fields.
    """
    return UserDto(
        id=login_user.id,
        email=login_user.email,
        role=login_user.role,
        is_active=login_user.is_active,
        updated_at=login_user.updated_at,
        created_at=login_user.created_at,
        login_at=login_user.login_at,
        privilege_names=privilege_names if privilege_names else []
    )


def inventory_optimization_to_dto(
        inventory_optimization: InventoryOptimization,
        user_id: int
) -> InventoryOptimizationDto:
    """
    Convert an InventoryOptimization model instance into an InventoryOptimizationDto.

    :param inventory_optimization: InventoryOptimization
        The Django model instance containing inventory optimization data.
    :param user_id: int
        The user ID required for ERP API calls.
    :return: InventoryOptimizationDto
        A DTO containing the mapped data from the model and external ERP data.
    :raises ValueError: If no SKU metric records or ERP data are found.
    """

    # Get injected service instances
    sku_metric_service = inject.instance(SkuMetricServiceInterface)
    erp_facade = inject.instance(ErpDevelopmentServiceFacadeInterface)

    def _get_sku_name_by_sku_number(
            sku_number: int,
            user_id: int
    ) -> str:
        """
        Retrieve the SKU name for the given sku_number by performing these steps:
          1. Retrieve local SKU record IDs using the SKU Metric service.
          2. Call the ERP service facade to retrieve the most recent SKU order record data.
          3. Return the 'sku_name' from the ERP data.

        :param sku_number: int
            The SKU number for which to obtain the SKU name.
        :param user_id: int
            The user ID required to identify the correct ERP configuration.
        :return: str
            The SKU name retrieved from the ERP data.
        :raises ValueError: If no SKU metric records are found or SKU name is missing in ERP data.
        """
        record_ids = sku_metric_service.get_all_sku_order_record_ids_by_sku_number(sku_number)
        if not record_ids:
            raise ValueError(f"No SkuMetric records found for sku_number={sku_number}.")
        erp_data = erp_facade.get_most_recent_sku_order_record(record_ids, user_id)
        if not erp_data or "sku_name" not in erp_data:
            raise ValueError("SKU name not found in ERP data.")
        return erp_data["sku_name"]

    return InventoryOptimizationDto(
        id=inventory_optimization.id,
        sku_number=inventory_optimization.sku_number,
        sku_name=_get_sku_name_by_sku_number(inventory_optimization.sku_number, user_id),
        order_quantity_q=inventory_optimization.order_quantity_q,
        reorder_point_r=inventory_optimization.reorder_point_r,
        holding_cost=inventory_optimization.holding_cost,
        setup_transportation_cost=inventory_optimization.setup_transportation_cost,
        stockout_cost=inventory_optimization.stockout_cost,
        total_cost=inventory_optimization.total_cost,
        order_frequency=inventory_optimization.order_frequency,
        cycle_time=inventory_optimization.cycle_time,
        is_custom=inventory_optimization.is_custom,
        updated_at=inventory_optimization.updated_at,
        inventory_record_id=inventory_optimization.inventory_record_id,
        user_id=inventory_optimization.user.id
    )
