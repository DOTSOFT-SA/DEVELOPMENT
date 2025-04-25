"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author1: EKETA (CERTH) - Ι.ΜΕΤ. (HIT)
 * Contributor: Georgios Karanasios R&D Software Engineer
 */
"""
import asyncio
import io
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge, BayesianRidge
from sklearn.metrics import mean_absolute_percentage_error, mean_absolute_error
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import OneHotEncoder
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from models.models import MlModel, UserErpApi
from repositories.ml_repositories import MlModelRepository
from repositories.user_erp_api_repository import UserErpApiRepository
from repositories.user_repository import UserRepository
from services.create_df_development import create_df_development
from utils.constants import SKU_ORDER_QUANTITY_PREDICTION_MODEL_TYPE
from utils.database_connection import AsyncSessionLocal


def _preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values, encode categorical columns, and extract 'week' from 'order_date'.
    This mirrors the original snippet's data-loading approach but uses the in-memory DataFrame.

    @param df: The DataFrame to preprocess.
    @return: The processed DataFrame with encoded categorical values and imputed missing data.
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
    # One-hot encode categorical columns (if any)
    if categorical_columns:
        encoder = OneHotEncoder(handle_unknown='ignore')
        encoded = encoder.fit_transform(df[categorical_columns]).toarray()
        category_labels = encoder.get_feature_names_out(categorical_columns)
        encoded_df = pd.DataFrame(encoded, columns=category_labels, index=df.index)
        df = pd.concat([df.drop(categorical_columns, axis=1), encoded_df], axis=1)
    # Return final DataFrame
    return df


def _train_and_best(df: pd.DataFrame) -> tuple[str, object, float, float]:
    """
    Train multiple regression models using RandomizedSearchCV, select the best model based on
    the lowest Mean Absolute Error (MAE), and return model performance metrics.

    @param df: The preprocessed DataFrame used for training and prediction.
    @return:
        - best_model_name: str -> Name of the best model.
        - best_model: Fitted model object -> The trained model.
        - best_mape: float -> Mean Absolute Percentage Error of the best model.
        - best_mae: float -> Mean Absolute Error of the best model.
    """

    # Separate features (X) and target (y)
    if 'order_item_unit_count' not in df.columns:
        # If order_item_unit_count doesn't exist, no training target is available
        raise ValueError("DataFrame must include 'order_item_unit_count' as the target column.")

    X = df.drop('order_item_unit_count', axis=1)
    y = df['order_item_unit_count']

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Define parameter distributions for RandomizedSearchCV
    param_distributions = {
        'RandomForestRegressor': {
            'n_estimators': [100, 200, 300],
            'max_depth': [None, 10, 20, 30],
            'min_samples_leaf': [1, 2, 4]
        },
        'DecisionTreeRegressor': {
            'max_depth': [None, 10, 20, 30],
            'min_samples_leaf': [1, 2, 4]
        },
        'LinearRegression': {},
        'Ridge': {
            'alpha': np.logspace(-4, 4, 10)
        },
        'BayesianRidge': {
            'alpha_1': np.logspace(-6, -1, 6),
            'alpha_2': np.logspace(-6, -1, 6),
            'lambda_1': np.logspace(-6, -1, 6),
            'lambda_2': np.logspace(-6, -1, 6)
        },
        'SVR': {
            'C': np.logspace(-4, 4, 9),
            'gamma': ['scale', 'auto']
        },
        'XGBRegressor': {
            'n_estimators': [100, 200],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.01, 0.1, 0.2]
        }
    }

    # Define models
    models = {
        "RandomForestRegressor": RandomForestRegressor(),
        "XGBRegressor": XGBRegressor(),
        "DecisionTreeRegressor": DecisionTreeRegressor(),
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(),
        "BayesianRidge": BayesianRidge(),
        "SVR": SVR()
    }

    # Train and evaluate each model
    results = {}
    for name, model in models.items():
        search = RandomizedSearchCV(model, param_distributions[name], n_iter=10, cv=5,
                                    scoring='neg_mean_absolute_error', random_state=42)
        search.fit(X_train, y_train)
        y_pred = search.best_estimator_.predict(X_test)
        mape = mean_absolute_percentage_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        results[name] = (search.best_estimator_, mape, mae)

    best_model_name = min(results, key=lambda x: results[x][2])  # Select based on the lowest MAE
    best_model = results[best_model_name][0]
    best_mape = results[best_model_name][1]  # Retrieve MAPE of the best model
    best_mae = results[best_model_name][2]

    return best_model_name, best_model, best_mape, best_mae


async def train_sku_order_quantity_prediction_model(
        df: pd.DataFrame,
        user_id: int
) -> None:
    """
    1. Preprocess the DataFrame.
    2. Train multiple models and select the best.
    3. Save the best model locally and then load it as bytes.
    4. Store the model along with its performance metrics and expected feature list in the database.

    @param df: The (df_development) DataFrame used as input for the ML algorithm.
    @param user_id: The ID of the user to whom the predictions correspond.
    @return: None
    """

    # 1. Preprocess the data
    df_processed = _preprocess_data(df)
    # Store the list of expected feature names (excluding the target column)
    model_features = df_processed.drop("order_item_unit_count", axis=1).columns.tolist()
    model_features_json = json.dumps(model_features)  # serialize as JSON
    # 2. Train and select the best model
    best_model_name, best_model, best_mape, best_mae = _train_and_best(df_processed)
    # 3. Serialize the model in memory
    buffer = io.BytesIO()
    joblib.dump(best_model, buffer)
    model_bytes = buffer.getvalue()
    # 4. Store the model, performance metrics, and expected features in the database.
    async with AsyncSessionLocal() as session:
        ml_repo = MlModelRepository(session)
        ml_model_data = MlModel(
            user_id=user_id,
            model_type=SKU_ORDER_QUANTITY_PREDICTION_MODEL_TYPE,
            model_name=best_model_name,
            model_file=model_bytes,
            mape=best_mape,
            mae=best_mae,
            model_features=model_features_json
        )
        # Insert or update in DB
        await ml_repo.create_or_update_ml_model(ml_model_data)
        print(f"Model successfully stored in the database with MAPE: {best_mape}, MAE: {best_mae}")


async def run_sku_order_quantity_prediction(user_erp_api: UserErpApi) -> None:
    """
    Main entry point for running the entire prediction pipeline:

    1. Build relevant URLs from configs.
    2. Call create_df_development to get the DataFrame.
    3. Run the SKU quantity prediction routine on that DataFrame.

    @param user_erp_api: A 'UserErpApi' object containing ERP API configuration for the user.
    @return: None
    """
    user_id = user_erp_api.user_id
    # Check if the user exists and is active using the existing UserRepository logic
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        # Run the process only for users that exists or active
        if not await user_repo.is_user_exist_and_active_by_id(user_id):
            raise ValueError(
                f"run_sku_order_quantity_prediction(): "
                f"User with ID {user_id} does not exist (or inactive) in the database."
            )
    # Build URLs based on the ERP API configuration (data) from the database.
    start_order_date = "?start_order_date=2023-01-01T00:00:00"  # Get data from 2023 onward
    erp_api_get_sku_order_development_url = user_erp_api.sku_order_url
    full_erp_api_get_sku_order_development_url = f"{erp_api_get_sku_order_development_url}{start_order_date}"
    auth_url = user_erp_api.login_token_url
    # Create the Development DataFrame
    df = await create_df_development(full_erp_api_get_sku_order_development_url, auth_url, user_id)
    if df.empty:
        print("No data received (by ERP or SKUMetric). Exiting.")
        return
    else:
        print("Development DataFrame temporarily created for 'SKU_Order_Quantity_Prediction' model")
    # Run the prediction routine
    await train_sku_order_quantity_prediction_model(df, user_id)


async def main() -> None:
    """
    Execute the SKU quantity prediction process for all users that have an ERP API configuration.
    @return: None
    """
    async with AsyncSessionLocal() as session:
        user_erp_repo = UserErpApiRepository(session)
        user_erp_api_list = await user_erp_repo.find_all_user_erp_api()

    if not user_erp_api_list:
        print("No ERP API configurations found. Exiting.")
        return

    # Iterate over each ERP API configuration
    for user_erp_api in user_erp_api_list:
        await run_sku_order_quantity_prediction(user_erp_api)


if __name__ == "__main__":
    asyncio.run(main())
