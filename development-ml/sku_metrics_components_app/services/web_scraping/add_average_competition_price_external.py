"""
/*
 * Copyright 2024 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import time
from typing import List, Optional

import pandas as pd
from selenium.webdriver.common.by import By
from sqlalchemy.ext.asyncio import AsyncSession

from models.dto_models import Product
from models.models import SkuMetric
from repositories.sku_metric_repository import SkuMetricRepository
from services.web_scraping.shared import restart_driver, setup_driver, get_best_matching_product
from utils.database_connection import AsyncSessionLocal


def collect_prices(driver, product: Product) -> Optional[float]:
    """
    Collects prices from the product page and calculates the average price.

    @param driver: The Selenium WebDriver.
    @param product: The Product object containing product details.
    @return: The average price of the product, or None if no price is found.
    """

    if not product.product_url:
        return None
    new_driver = restart_driver(driver)  # Restart the WebDriver (trick to avoid CAPTCHA)
    new_driver.get(product.product_url + "#shops")  # Navigate to the product page with #shops
    time.sleep(10)  # Wait to load the page fully
    avg_price = None
    try:
        # Collect price elements
        price_elements = new_driver.find_elements(By.CSS_SELECTOR,
                                                  'strong.dominant-price[data-e2e-testid="dominant-price"]')
        # Extract and convert the text of each price element to a float
        prices = [float(p.text.replace('€', '').replace(',', '.').strip()) for p in price_elements]
        if prices:
            avg_price = round(sum(prices) / len(prices), 2)  # Calculate the average price with 2 decimal places format
    except Exception as e:
        print(f"Could not collect competitor prices for {product.product_title}\n{e}")
    finally:
        new_driver.quit()
    return avg_price


async def process_web_scraping_prices(session: AsyncSession, erp_sku_order_development_data: List[dict]) -> None:
    """
    Processes web scraping for competitor prices by filtering records
    with missing price data and scraping the necessary information.

    1. Filter DB for records that do NOT have average_competition_price_external
    2. For each record, scrape competitor reviews.

    @param session: The asynchronous database session.
    @param erp_sku_order_development_data: List of dictionaries containing SKU order development data.
    """

    # Initialize the repositories for SKU metrics
    sku_metric_repo = SkuMetricRepository(session)
    # We want to process only records that have NULL in these columns
    filtered_erp_sku_order_development_data = await sku_metric_repo.filter_in_db_with_null_columns(
        erp_sku_order_development_data,
        db_null_column_names=["average_competition_price_external"],
        db_identity_unique_col_name="sku_order_record_id"
    )
    if not filtered_erp_sku_order_development_data:
        print("No rows found with NULL 'average_competition_price_external'. Nothing to scrape.")
        return
    # Convert to DataFrame for convenience
    df = pd.DataFrame(filtered_erp_sku_order_development_data)
    for _, row in df.iterrows():
        record_id = row["id"]  # ERP data's 'id'
        sku_number = row.get("sku_number")
        sku_name = row.get("sku_name")
        # print(f"\nScraping for SKU: {sku_name}, record_id: {record_id}")
        # This returns a configured Selenium WebDriver to run in the browser (or terminal)
        driver = setup_driver()
        try:
            # 1. # Retrieve the best matching product data for the current SKU
            product = await get_best_matching_product(driver, sku_number, sku_name, record_id)
            if not product.product_url:
                print(f"No valid best product URL found for {sku_name}. Skipping price scraping.")
                continue
            # 2. Collect price data
            avg_price = collect_prices(driver, product)
            # 3. Update DB
            sku_metric = SkuMetric(
                sku_order_record_id=record_id,
                average_competition_price_external=avg_price,
            )
            # Update the values in the DB
            await sku_metric_repo.update_sku_metric_average_competition_price_external(sku_metric)
        except Exception as e:
            print(f"Error processing SKU: {sku_name}, Error: {e}")
        finally:
            driver.quit()
    print("'average_competition_price_external' was added successfully in sku_metric.")


async def main(erp_sku_order_development_data: list):
    try:
        async with AsyncSessionLocal() as session:
            await process_web_scraping_prices(session, erp_sku_order_development_data)
    except Exception as e:
        await session.rollback()
        raise e
