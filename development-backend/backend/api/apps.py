"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import logging

import inject
from django.apps import AppConfig

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ApiConfig(AppConfig):
    """
    Django application configuration class for the API app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        """
        Configure dependency injection bindings for repositories and services.
        """

        def config(binder):
            # Move imports here to avoid AppRegistryNotReady errors
            from .repositories.user_repository_interface import UserRepositoryInterface
            from .repositories.user_repository import UserRepository

            from .repositories.user_privilege_repository_interface import UserPrivilegeRepositoryInterface
            from .repositories.user_privilege_repository import UserPrivilegeRepository

            from .repositories.sku_order_quantity_prediction_repository_interface import \
                SkuOrderQuantityPredictionRepositoryInterface
            from .repositories.sku_order_quantity_prediction_repository import SkuOrderQuantityPredictionRepository

            from .repositories.inventory_optimization_repository_interface import \
                InventoryOptimizationRepositoryInterface
            from .repositories.inventory_optimization_repository import InventoryOptimizationRepository

            from .repositories.distribution_optimization_repository_interface import \
                DistributionOptimizationRepositoryInterface
            from .repositories.distribution_optimization_repository import DistributionOptimizationRepository

            from .repositories.sku_metric_repository_interface import SkuMetricRepositoryInterface
            from .repositories.sku_metric_repository import SkuMetricRepository

            from .repositories.ml_model_repository_interface import MLModelRepositoryInterface
            from .repositories.ml_model_repository import MLModelRepository

            from .repositories.erp_development_repository import ErpDevelopmentRepository
            from .repositories.erp_development_repository_interface import ErpDevelopmentRepositoryInterface

            from .repositories.user_erp_api_repository import UserErpApiRepository
            from .repositories.user_erp_api_repository_interface import UserErpApiRepositoryInterface

            # Import Services
            from .services.user_service_interface import UserServiceInterface
            from .services.user_service import UserService

            from .services.user_privilege_service_interface import UserPrivilegeServiceInterface
            from .services.user_privilege_service import UserPrivilegeService

            from .services.sku_order_quantity_prediction_service_interface import \
                SkuOrderQuantityPredictionServiceInterface
            from .services.sku_order_quantity_prediction_service import SkuOrderQuantityPredictionService

            from .services.inventory_optimization_service_interface import InventoryOptimizationServiceInterface
            from .services.inventory_optimization_service import InventoryOptimizationService

            from .services.distribution_optimization_service_interface import DistributionOptimizationServiceInterface
            from .services.distribution_optimization_service import DistributionOptimizationService

            from .services.sku_metric_service_interface import SkuMetricServiceInterface
            from .services.sku_metric_service import SkuMetricService

            from .services.ml_model_service_interface import MLModelServiceInterface
            from .services.ml_model_service import MLModelService

            from .services.inventory_service_interface import InventoryServiceInterface
            from .services.inventory_service import InventoryService

            from .services.distribution_optimization_with_traffic_service_interface import \
                DistributionOptimizationWithTrafficServiceInterface
            from .services.distribution_optimization_with_traffic_service import \
                DistributionOptimizationWithTrafficService

            from .services.user_erp_api_service import UserErpApiService
            from .services.user_erp_api_service_interface import UserErpApiServiceInterface

            # Import Facades
            from .services.facades.user_privilege_service_facade_interface import UserPrivilegeServiceFacadeInterface
            from .services.facades.user_privilege_service_facade import UserPrivilegeServiceFacade
            from .services.facades.model_inference_service_facade_interface import ModelInferenceServiceFacadeInterface
            from .services.facades.model_inference_service_facade import ModelInferenceServiceFacade
            from .services.facades.inventory_service_facade_interface import InventoryServiceFacadeInterface
            from .services.facades.inventory_service_facade import InventoryServiceFacade
            from .services.facades.distribution_optimization_routing_facade_interface import \
                DistributionOptimizationRoutingFacadeInterface
            from .services.facades.distribution_optimization_routing_facade import DistributionOptimizationRoutingFacade
            from .services.facades.erp_development_service_facade_interface import ErpDevelopmentServiceFacadeInterface
            from .services.facades.erp_development_service_facade import ErpDevelopmentServiceFacade

            # Bind Repositories
            binder.bind(UserRepositoryInterface, UserRepository)
            binder.bind(UserPrivilegeRepositoryInterface, UserPrivilegeRepository)
            binder.bind(SkuMetricRepositoryInterface, SkuMetricRepository)
            binder.bind(SkuOrderQuantityPredictionRepositoryInterface, SkuOrderQuantityPredictionRepository)
            binder.bind(InventoryOptimizationRepositoryInterface, InventoryOptimizationRepository)
            binder.bind(DistributionOptimizationRepositoryInterface, DistributionOptimizationRepository)
            binder.bind(MLModelRepositoryInterface, MLModelRepository)
            binder.bind(ErpDevelopmentRepositoryInterface, ErpDevelopmentRepository)
            binder.bind(UserErpApiRepositoryInterface, UserErpApiRepository)

            # Bind Services
            binder.bind_to_constructor(
                UserServiceInterface,
                lambda: UserService(inject.instance(UserRepositoryInterface))
            )
            binder.bind_to_constructor(
                UserPrivilegeServiceInterface,
                lambda: UserPrivilegeService(inject.instance(UserPrivilegeRepositoryInterface))
            )
            binder.bind_to_constructor(
                SkuOrderQuantityPredictionServiceInterface,
                lambda: SkuOrderQuantityPredictionService(
                    inject.instance(SkuOrderQuantityPredictionRepositoryInterface)
                )
            )
            binder.bind_to_constructor(
                InventoryOptimizationServiceInterface,
                lambda: InventoryOptimizationService(
                    inject.instance(InventoryOptimizationRepositoryInterface)
                )
            )
            binder.bind_to_constructor(
                DistributionOptimizationServiceInterface,
                lambda: DistributionOptimizationService(
                    inject.instance(DistributionOptimizationRepositoryInterface)
                )
            )
            binder.bind_to_constructor(
                MLModelServiceInterface,
                lambda: MLModelService(inject.instance(MLModelRepositoryInterface))
            )
            binder.bind_to_constructor(
                SkuMetricServiceInterface,
                lambda: SkuMetricService(inject.instance(SkuMetricRepositoryInterface))
            )
            binder.bind_to_constructor(
                InventoryServiceInterface,
                lambda: InventoryService()
            )
            binder.bind_to_constructor(
                DistributionOptimizationWithTrafficServiceInterface,
                lambda: DistributionOptimizationWithTrafficService()
            )
            binder.bind_to_constructor(
                UserErpApiServiceInterface,
                lambda: UserErpApiService(inject.instance(UserErpApiRepositoryInterface))
            )

            # Bind Facades
            binder.bind_to_constructor(
                UserPrivilegeServiceFacadeInterface,
                lambda: UserPrivilegeServiceFacade(
                    inject.instance(UserServiceInterface),
                    inject.instance(UserPrivilegeServiceInterface),
                    inject.instance(UserErpApiServiceInterface)
                )
            )
            binder.bind_to_constructor(
                ErpDevelopmentServiceFacadeInterface,
                lambda: ErpDevelopmentServiceFacade(
                    inject.instance(ErpDevelopmentRepositoryInterface),
                    inject.instance(UserErpApiServiceInterface),
                    inject.instance(SkuMetricServiceInterface)
                )
            )
            binder.bind_to_constructor(
                ModelInferenceServiceFacadeInterface,
                lambda: ModelInferenceServiceFacade(
                    inject.instance(ErpDevelopmentServiceFacadeInterface),
                    inject.instance(MLModelServiceInterface),
                    inject.instance(SkuOrderQuantityPredictionServiceInterface),
                    inject.instance(SkuMetricServiceInterface)
                )
            )
            binder.bind_to_constructor(
                InventoryServiceFacadeInterface,
                lambda: InventoryServiceFacade(
                    inject.instance(ErpDevelopmentServiceFacadeInterface),
                    inject.instance(SkuOrderQuantityPredictionServiceInterface),
                    inject.instance(SkuMetricServiceInterface),
                    inject.instance(InventoryServiceInterface),
                    inject.instance(InventoryOptimizationServiceInterface),
                    inject.instance(ModelInferenceServiceFacadeInterface),
                )
            )
            binder.bind_to_constructor(
                DistributionOptimizationRoutingFacadeInterface,
                lambda: DistributionOptimizationRoutingFacade(
                    inject.instance(ErpDevelopmentServiceFacadeInterface),
                    inject.instance(DistributionOptimizationWithTrafficServiceInterface),
                    inject.instance(DistributionOptimizationServiceInterface)
                )
            )

            # logger.info("Dependency injection bindings configured successfully.")

        # Ensure configuration happens once
        inject.configure_once(config)
