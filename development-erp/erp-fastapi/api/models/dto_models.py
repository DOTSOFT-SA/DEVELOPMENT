"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import Union, List, Optional

from pydantic import BaseModel

from api.models.models import SkuOrderDevelopment, InventoryParamsDevelopment


class ResponseWithUserID(BaseModel):
    user_id: int
    data: Union[List, dict]


class ResponseSkuOrderDevelopmentWithUserID(BaseModel):
    user_id: int
    data: SkuOrderDevelopment


class ResponseInventoryParamsDevelopmentWithUserID(BaseModel):
    user_id: int
    data: Optional[InventoryParamsDevelopment] = None


class ListIdsDTO(BaseModel):
    ids: List[int] = []


class InventoryParamsDTO(BaseModel):
    sku_number: int
