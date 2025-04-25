"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from api.views.distribution_optimization_viewset import DistributionOptimizationViewSet
from api.views.erp_development_viewset import ErpDevelopmentViewSet
from api.views.inventory_optimization_viewset import InventoryOptimizationViewSet
from api.views.predictions_viewset import PredictionsViewSet
from api.views.sku_order_quantity_prediction_viewset import SkuOrderQuantityPredictionViewSet
from api.views.user_erp_api_viewset import UserErpApiViewSet
from api.views.user_viewset import UserViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter

""" REGISTER ROUTES HERE """
router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'', SkuOrderQuantityPredictionViewSet, basename='skuOrderQuantityPredictionViewSet')
router.register(r'', InventoryOptimizationViewSet, basename='inventoryOptimizationViewSet')
router.register(r'', DistributionOptimizationViewSet, basename='distributionOptimizationViewSet')
router.register(r'', ErpDevelopmentViewSet, basename='erpSkuMetric')
router.register(r'', PredictionsViewSet, basename='modelInference')
router.register(r'user', UserErpApiViewSet, basename='userErpApi')

urlpatterns = [
    # All API routes are prefixed with 'api/'
    path('api/', include(router.urls)),  # Include all ViewSet routes
]
