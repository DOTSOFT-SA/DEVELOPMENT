"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import logging

from django.core.exceptions import ObjectDoesNotExist

from .ml_model_repository_interface import MLModelRepositoryInterface
from ..models.ml_model import MLModel

logger = logging.getLogger(__name__)


class MLModelRepository(MLModelRepositoryInterface):

    @staticmethod
    def find_model_file_by_user_and_name(user_id: int, model_type: str) -> MLModel | None:
        """
        Retrieve the stored model file (binary) for a given user_id and model_type.

        :param user_id: int: The ID of the user who owns the model.
        :param model_type: str: The type of the model to retrieve.
        :return: MLModel | None: The MLModel object if found, otherwise None.
        """
        try:
            model = MLModel.objects.get(user_id=user_id, model_type=model_type)
            return model
        except ObjectDoesNotExist:
            return None
