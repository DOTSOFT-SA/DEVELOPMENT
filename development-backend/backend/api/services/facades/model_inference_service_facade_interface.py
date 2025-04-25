"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod

from ...models.dtos.model_inference_dto import ModelInferenceDto


class ModelInferenceServiceFacadeInterface(ABC):
    """
    Interface for the ModelInferenceServiceFacade, defining the contract for model inference.
    """

    @abstractmethod
    def run_sku_order_quantity_inference(self, sku_number: int, user_id: int) -> ModelInferenceDto:
        pass
