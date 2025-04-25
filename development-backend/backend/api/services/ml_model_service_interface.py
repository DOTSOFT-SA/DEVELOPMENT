"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod

from ..models.ml_model import MLModel


class MLModelServiceInterface(ABC):

    @abstractmethod
    def get_trained_model(self, user_id: int, model_type: str) -> MLModel:
        pass
