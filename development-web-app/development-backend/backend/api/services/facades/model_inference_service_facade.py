"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import json
import logging
from io import BytesIO
from typing import Optional

import inject
import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder

from .erp_development_service_facade_interface import ErpDevelopmentServiceFacadeInterface
from .model_inference_service_facade_interface import ModelInferenceServiceFacadeInterface
from ..sku_metric_service_interface import SkuMetricServiceInterface
from ...models.dtos.merged_sku_metric_dto import MergedSkuMetricDto
from ...models.dtos.model_inference_dto import ModelInferenceDto
from ...models.sku_order_quantity_prediction import SkuOrderQuantityPrediction
from ...services.ml_model_service_interface import MLModelServiceInterface
from ...services.sku_order_quantity_prediction_service_interface import SkuOrderQuantityPredictionServiceInterface
from ...utils.enums import MLModelName

logger = logging.getLogger(__name__)


class ModelInferenceServiceFacade(ModelInferenceServiceFacadeInterface):
    """
    Facade to run inference on a given SKU number for the 'sku_order_quantity_prediction' model,
    returning a SkuOrderQuantityPredictionDTO and the MergedSkuMetricDto.
    """

    @inject.autoparams()
    def __init__(self,
                 erp_sku_metric_service: ErpDevelopmentServiceFacadeInterface,
                 ml_model_service: MLModelServiceInterface,
                 sku_order_quantity_prediction_service: SkuOrderQuantityPredictionServiceInterface,
                 sku_metric_service: SkuMetricServiceInterface):
        """
        Constructor injection of the required services.
        """
        self.erp_sku_metric_service = erp_sku_metric_service
        self.ml_model_service = ml_model_service
        self.prediction_service = sku_order_quantity_prediction_service
        self.sku_metric_service = sku_metric_service

    def run_sku_order_quantity_inference(self, sku_number: int, user_id: int) -> ModelInferenceDto:
        """
        Runs inference for SKU order quantity prediction.

        Steps:
        1) Fetch merged SKU metric data.
        2) Load trained model and preprocess input (load with joblib).
        3) Run inference and store predictions in the database.
        4) Return the model inference results (merged_sku_metric_dto, SkuOrderQuantityPredictionDTO).

        :param sku_number: int: The SKU number for which inference is performed.
        :param user_id: int: The user ID requesting the inference.
        :return: ModelInferenceDto: An object containing the merged SKU metric data and the inference results.
        :raises ValueError: If no merged SKU metric data is available.
        """
        # Step 1: Get Merged data
        merged_sku_metric_dto: Optional[MergedSkuMetricDto] = self.erp_sku_metric_service.get_merged_sku_metric_info(
            sku_number,
            user_id)
        if not merged_sku_metric_dto:
            logger.warning("No merged data returned, cannot proceed with inference.")
            raise
        # Step 2: Load model and run prediction
        model_name, predicted_value, model_mape, model_mae = self._run_inference(user_id, merged_sku_metric_dto)
        # Step 3: Store the result in sku_order_quantity_prediction
        new_sku_order_quantity_prediction = SkuOrderQuantityPrediction(
            model_name=model_name,
            sku_number=merged_sku_metric_dto.sku_number,
            week_number=pd.Timestamp(merged_sku_metric_dto.order_date).isocalendar().week,
            year_of_the_week=pd.Timestamp(merged_sku_metric_dto.order_date).isocalendar().year,
            predicted_value=predicted_value,
            mae=model_mae,
            mape=model_mape,
            sku_order_record=self.sku_metric_service.get_by_sku_order_record_id(
                merged_sku_metric_dto.sku_order_record_id),
            user_id=user_id
        )
        self.prediction_service.create_sku_order_quantity_prediction(new_sku_order_quantity_prediction)
        # return a ModelInferenceDto:
        return ModelInferenceDto(
            merged_sku_metric_dto=merged_sku_metric_dto,
            sku_order_quantity_prediction=new_sku_order_quantity_prediction
        )

    @staticmethod
    def _preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values, encode categorical columns, and extract 'week' from 'order_date'.

        :param df: pd.DataFrame: The DataFrame to preprocess.
        :return: pd.DataFrame: The processed DataFrame with encoded categorical values and imputed missing data.
        """

        # Convert 'order_date' to datetime and extract 'week'
        if 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
            df['week'] = df['order_date'].dt.isocalendar().week
            df.drop('order_date', axis=1, inplace=True)
        # Separate numeric and categorical columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = list(set(df.columns) - set(numeric_columns))
        # Impute numeric columns
        df[numeric_columns] = SimpleImputer(strategy='mean').fit_transform(df[numeric_columns])
        # One-hot encode categorical columns
        if categorical_columns:
            encoder = OneHotEncoder(handle_unknown='ignore')
            encoded = encoder.fit_transform(df[categorical_columns]).toarray()
            category_labels = encoder.get_feature_names_out(categorical_columns)
            encoded_df = pd.DataFrame(encoded, columns=category_labels, index=df.index)
            df = pd.concat([df.drop(categorical_columns, axis=1), encoded_df], axis=1)
        # Return final DataFrame
        return df

    def _build_feature_vector(self, model_features, merged_sku_metric_dto: MergedSkuMetricDto) -> pd.DataFrame:
        """
        Builds a feature vector for inference using the stored model features.

        :param model_features: list: The expected feature columns used during model training.
        :param merged_sku_metric_dto: MergedSkuMetricDto: The DTO containing SKU-related data.
        :return: pd.DataFrame: A processed DataFrame with features aligned to the trained model's expectations.
        """

        # Prepare a DataFrame from the merged DTO.
        order_date_parsed = pd.Timestamp(merged_sku_metric_dto.order_date)
        input_data = {
            "week": order_date_parsed.isocalendar().week,
            "sku_name": merged_sku_metric_dto.sku_name,
            "class_display_name": merged_sku_metric_dto.class_display_name,
            "order_item_price_in_main_currency": merged_sku_metric_dto.order_item_price_in_main_currency,
            "order_item_unit_count": merged_sku_metric_dto.order_item_unit_count,
            "cl_price": merged_sku_metric_dto.cl_price,
            "is_weekend": int(merged_sku_metric_dto.is_weekend),
            "is_holiday": int(merged_sku_metric_dto.is_holiday),
            "mean_temperature": merged_sku_metric_dto.mean_temperature,
            "rain": int(merged_sku_metric_dto.rain),
            "average_competition_price_external": merged_sku_metric_dto.average_competition_price_external,
            "review_sentiment_score": merged_sku_metric_dto.review_sentiment_score,
            "trend_value": merged_sku_metric_dto.trend_value,
        }

        input_df = pd.DataFrame([input_data])
        # Preprocess the input using the same _preprocess_data function.
        input_processed = self._preprocess_data(input_df)
        # **Crucial step:** re-index the preprocessed input to match the expected training features.
        input_processed = input_processed.reindex(columns=model_features, fill_value=0)

        return input_processed

    def _run_inference(self, user_id, merged_sku_metric_dto: MergedSkuMetricDto) -> tuple[str, float, float, float] | \
                                                                                    tuple[MergedSkuMetricDto, None]:
        """
        Runs the inference process for SKU order quantity prediction.

        :param user_id: int: The ID of the user requesting inference.
        :param merged_sku_metric_dto: MergedSkuMetricDto: The DTO containing SKU-related data.
        :return: tuple[str, float, float, float] | tuple[MergedSkuMetricDto, None]:
                 - If successful, returns a tuple with:
                   - Model name (str)
                   - Predicted value (float)
                   - MAPE (Mean Absolute Percentage Error) (float)
                   - MAE (Mean Absolute Error) (float)
                 - If model loading fails, returns a tuple with:
                   - MergedSkuMetricDto (original input)
                   - None
        :raises ValueError: If an error occurs during model prediction.
        """
        # Retrieve MLModel record
        ml_model = self.ml_model_service.get_trained_model(user_id,
                                                           MLModelName.SKU_ORDER_QUANTITY_PREDICTION_MODEL.value)
        # Retrieve the model features used in training
        model_features = json.loads(ml_model.model_features)
        # Load the trained model
        try:
            loaded_model = joblib.load(BytesIO(ml_model.model_file))
        except Exception as e:
            logger.error(f"Failed to load joblib model: {str(e)}")
            return merged_sku_metric_dto, None
        # We also retrieve the stored mape & mae from the MLModel
        model_mape = ml_model.mape
        model_mae = ml_model.mae
        # Prepare features for inference (collecting them into a list or array)
        input_data = self._build_feature_vector(model_features, merged_sku_metric_dto)
        # Inference
        try:
            predicted_value = loaded_model.predict(input_data.values)[0]
        except Exception as e:
            logger.error(f"Error during predict(): {e}")
            raise
        logger.info(f"Inference predicted_value={predicted_value}")
        # Return
        return ml_model.model_name, predicted_value, model_mape, model_mae
