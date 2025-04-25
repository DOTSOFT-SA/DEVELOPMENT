"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import logging

import inject

from .ml_model_service_interface import MLModelServiceInterface
from ..models.ml_model import MLModel
from ..repositories.ml_model_repository_interface import MLModelRepositoryInterface

logger = logging.getLogger(__name__)


class MLModelService(MLModelServiceInterface):

    @inject.autoparams()
    def __init__(self, ml_model_repository: MLModelRepositoryInterface):
        """
        Initialize the MLModelService with its repository.
        """
        self.ml_model_repository = ml_model_repository

    def get_trained_model(self, user_id: int, model_type: str) -> MLModel:
        """
        Calls the repository to retrieve the model file.

        :param user_id: int: The ID of the user who owns the model.
        :param model_type: str: The type of the model.
        :return: MLModel: The MLModel instance if found.
        :raises ValueError: If no model is found for the given user_id and model_type.
        """
        ml_model = self.ml_model_repository.find_model_file_by_user_and_name(user_id, model_type)
        if not ml_model:
            logger.warning(f"No ML model found for user_id={user_id} and model_type='{model_type}'.")
            raise ValueError("ML model not found in DB.")
        return ml_model
