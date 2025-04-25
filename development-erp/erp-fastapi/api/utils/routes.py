"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from fastapi import APIRouter, Depends

from ..controllers.auth_controller import router as auth_router, verify_jwt
from ..controllers.distribution_routing_controller import router as distribution_routing_router
from ..controllers.inventory_params_development_controller import router as inventory_params_development_router
from ..controllers.sku_order_development_controller import router as sku_order_development_router

# Create main router
api_router = APIRouter()

# Add your routes here
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(sku_order_development_router, prefix="/api", dependencies=[Depends(verify_jwt)])
api_router.include_router(inventory_params_development_router, prefix="/api", dependencies=[Depends(verify_jwt)])
api_router.include_router(distribution_routing_router, prefix="/api", dependencies=[Depends(verify_jwt)])
