"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod

from ..models.ml_model import MLModel


class MLModelRepositoryInterface(ABC):

    @abstractmethod
    def find_model_file_by_user_and_name(self, user_id: int, model_type: str) -> MLModel | None:
        pass
