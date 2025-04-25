"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""
import asyncio

from models.models import UserErpApi
from repositories.user_erp_api_repository import UserErpApiRepository
from services import add_holidays_weekends_weather, add_sku_number_user_id_sku_order_record_id, \
    fetch_erp_development_service, add_review_sentiment_score_and_timestamp
from services.google_trends import add_google_trends
from services.web_scraping import add_average_competition_price_external
from utils.database_connection import AsyncSessionLocal


async def run_step(step_func, step_name: str, *args):
    """
    Runs a given asynchronous step function with the provided arguments.
    Logs any exceptions that occur without interrupting subsequent steps.

    @param step_func: The async function that executes the step logic.
    @param step_name: A human-readable name for the step (for logging).
    @param args: Arguments to pass to the step function.
    """
    print(f"\nWe are at {step_name}")
    try:
        await step_func(*args)
    except Exception as e:
        print(f"Error in {step_name}: {e}")


async def run_steps(user_id: int, erp_sku_order_development_data: list) -> None:
    """
    Execute the data processing steps for SKU metrics.

    @params user_id: int
        The unique identifier of the user associated with the SKU order development data.
    @params erp_sku_order_development_data: list
        A list of dictionaries containing SKU order development data.
    """

    # Step 1: Populate 'sku_number', 'user_id', and 'sku_order_record_id' first
    await run_step(
        add_sku_number_user_id_sku_order_record_id.main,
        "Step 1 (add_sku_number_user_id_sku_order_record_id)",
        *[user_id, erp_sku_order_development_data]
    )
    # Step 2: Populate 'is_holiday', 'is_weekend', 'rain', 'mean_temperature' columns
    await run_step(
        add_holidays_weekends_weather.main,
        "Step 2 (add_holidays_weekends_weather)",
        erp_sku_order_development_data
    )
    # Step 3: Populate 'trend_value' column
    await run_step(
        add_google_trends.main,
        "Step 3 (add_google_trends)",
        erp_sku_order_development_data
    )
    # Step 4: Populate 'add_average_competition_price_external' column
    await run_step(
        add_average_competition_price_external.main,
        "Step 4 (add_average_competition_price_external)",
        erp_sku_order_development_data
    )
    # Step 5: Populate 'review_sentiment_score' & 'review_sentiment_timestamp' columns
    await run_step(
        add_review_sentiment_score_and_timestamp.main,
        "Step 5 (add_review_sentiment_score_and_timestamp)",
        erp_sku_order_development_data
    )


async def populate_sku_metrics_table(user_erp_api: UserErpApi):
    try:
        # Initialize URLs
        start_order_date = "?start_order_date=2023-01-01T00:00:00"  # Get data from 2023 and afterward
        erp_api_get_sku_order_development_url = user_erp_api.sku_order_url
        full_erp_api_get_sku_order_development_url = f"{erp_api_get_sku_order_development_url}{start_order_date}"
        auth_url = user_erp_api.login_token_url
        # Construct final URLs
        erp_sku_order_development_data = await fetch_erp_development_service.fetch_erp_development_data(
            full_erp_api_get_sku_order_development_url, auth_url, user_erp_api.user_id)
        # Start the data processing
        print(f"Processing data for user_id: {user_erp_api.user_id}")
        # # TODO: Delete next line after testing
        # erp_sku_order_development_data = erp_sku_order_development_data[3:4]  # 4th row
        await run_steps(user_erp_api.user_id, erp_sku_order_development_data)
        print(f"\nData processing has finished for user_id: {user_erp_api.user_id}")
    except Exception as e:
        print(f"Error in populate_sku_metrics_table for client with user id '{user_erp_api.user_id}': {e}")


async def main():
    try:
        async with AsyncSessionLocal() as session:
            user_erp_repo = UserErpApiRepository(session)
            user_erp_api_list = await user_erp_repo.find_all_user_erp_api()

        if not user_erp_api_list:
            print("No ERP API configurations found. Exiting.")
            return

        for user_erp_api in user_erp_api_list:  # Do the process for every client
            await populate_sku_metrics_table(user_erp_api)  # Populate the SKUMetrics table
    except Exception as e:
        print(f"{e}")


if __name__ == "__main__":
    asyncio.run(main())
