"""
/*
 * Copyright 2024 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import time
from typing import List

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from sqlalchemy.ext.asyncio import AsyncSession

from models.dto_models import Product, Review
from repositories.sku_metric_repository import SkuMetricRepository
from services.web_scraping.shared import setup_driver, get_best_matching_product, restart_driver
from utils.database_connection import AsyncSessionLocal


def get_review_data(driver: webdriver.Chrome, product: Product) -> List[Review]:
    """
    Retrieves review data from a product page.

    @param driver: The Selenium WebDriver.
    @param product: The Product object containing product details.
    @return: A list of Review objects.
    """

    # Initialization
    driver.get(product.product_url + "#reviews")  # Navigate to the product's URL reviews page
    time.sleep(10)  # Wait to load the page fully
    reviews = []
    try:
        review_list = driver.find_element(By.ID, 'sku_reviews_list')  # Locate the review list element by its ID
        review_elements = review_list.find_elements(By.CSS_SELECTOR, 'li[id^="sku_review"]')  # Find all review items
        for rev in review_elements:
            stars = rev.get_attribute('data-stars')  # Get the stars rating
            content = rev.find_element(By.CSS_SELECTOR, 'div.review-content')  # Locate the review data
            if content:
                # Extract review data: comment, pros, medium, bad, and no opinion details
                comment = content.find_element(By.CSS_SELECTOR, 'p').text
                pros = [li.text for li in rev.find_elements(By.CSS_SELECTOR, 'ul.icon.pros li')]
                medium = [li.text for li in rev.find_elements(By.CSS_SELECTOR, 'ul.icon.so-so li')]
                bad = [li.text for li in rev.find_elements(By.CSS_SELECTOR, 'ul.icon.bad li')]
                no_opinion = [li.text for li in rev.find_elements(By.CSS_SELECTOR, 'ul.icon.no-opinion li')]
                # Create a Review object and append it to the reviews list
                reviews.append(Review(product, stars, comment, pros, medium, bad, no_opinion))
        return reviews
    except Exception as e:
        print(f"Error retrieving reviews for product: {product.product_title}\n{e}")


def scrape_product_reviews(driver: webdriver.Chrome, product: Product) -> List[Review]:
    """
    Scrapes reviews from a product URL and stores the data.

    @param driver: The Selenium WebDriver.
    @param product: The Product object containing product details.
    @return: A list of Review objects retrieved from the product page.
    """
    if product.product_url:  # If product URL included, scrape reviews
        new_driver = restart_driver(driver)  # Restart the WebDriver (trick to avoid CAPTCHA)
        # print(f"Processing reviews for product: {product.product_title}")
        try:
            return get_review_data(new_driver, product)
        finally:
            new_driver.quit()


async def process_web_scraping_reviews(session: AsyncSession, erp_sku_order_development_data: List[dict]) -> list[
                                                                                                                 Review] | None:
    """
    Processes web scraping for product reviews.
    1. Filter DB for records that do NOT have review_sentiment_score, review_sentiment_timestamp.
    2. For each record, scrape reviews

    @param session: The asynchronous database session.
    @param erp_sku_order_development_data: List of dictionaries containing SKU order development data.
    """

    # Initialize the repositories for SKU metrics
    sku_metric_repo = SkuMetricRepository(session)
    # We want to process only records that have NULL in these columns
    filtered_erp_sku_order_development_data = await sku_metric_repo.filter_in_db_with_null_columns(
        erp_sku_order_development_data,
        db_null_column_names=["review_sentiment_score", "review_sentiment_timestamp"],
        db_identity_unique_col_name="sku_order_record_id"
    )
    if not filtered_erp_sku_order_development_data:
        print("No rows found with NULL 'review_sentiment_score' or 'review_sentiment_timestamp'. Nothing to scrape.")
        return
    # Convert to DataFrame for convenience
    df = pd.DataFrame(filtered_erp_sku_order_development_data)
    for _, row in df.iterrows():
        sku_order_record_id = row.get("id")  # ERP data's 'id'
        sku_number = row.get("sku_number")
        sku_name = row.get("sku_name")
        # print(f"\nScraping for SKU: {sku_name}, record_id: {record_id}")
        # This returns a configured Selenium WebDriver to run in the browser (or terminal)
        driver = setup_driver()
        # 1. # Retrieve the best matching product data for the current SKU
        product = await get_best_matching_product(driver, sku_number, sku_name, sku_order_record_id)
        if not product.product_url:
            print(f"No valid product URL found for {sku_name}. Skipping price & review scraping.")
            continue
        # 2. Collect product reviews
        product_reviews = scrape_product_reviews(driver, product)
        driver.quit()
        return product_reviews


async def main(erp_sku_order_development_data: list) -> list[Review] | None:
    try:
        async with AsyncSessionLocal() as session:
            return await process_web_scraping_reviews(session, erp_sku_order_development_data)
    except Exception as e:
        await session.rollback()
        raise e
