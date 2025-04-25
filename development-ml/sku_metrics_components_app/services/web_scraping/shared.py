"""
/*
 * Copyright 2024 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import os
import random
import time
import urllib.parse
from typing import List

from googletrans import Translator
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from sentence_transformers import SentenceTransformer, util

from models.dto_models import Product


def setup_driver() -> webdriver.Chrome:
    """
    Sets up and initializes the Selenium WebDriver with a random user agent.

    @return webdriver.Chrome: Configured Selenium WebDriver instance.
    """

    # Define a list of user agent strings (more user_agents = more chances to avoid CAPTCHA)
    user_agents_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:115.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (Linux; Android 11; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Android 10; Mobile; rv:115.0) Gecko/115.0 Chrome/114.0.5735.134",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:115.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Mobile Safari/537.36",
        "Mozilla/5.0 (Android 9; Mobile; LG-M255; rv:115.0) Gecko/115.0 Firefox/115.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:115.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12.6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36"
    ]
    user_agent = random.choice(user_agents_list)  # Choose a random user agent
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_argument("--headless")  # Uncomment if you want a headless browser
    chrome_options.add_argument("--use_subprocess")
    # Construct the path to the ChromeDriver dynamically
    root_path = os.getcwd()  # Get the root path of the project
    chrome_driver_path = os.path.join(root_path, "configs", 'chromedriver-win64', 'chromedriver.exe')
    service = Service(executable_path=chrome_driver_path)
    # Initialize the driver with the above options
    return webdriver.Chrome(service=service, options=chrome_options)


def restart_driver(driver: webdriver.Chrome) -> webdriver.Chrome:
    """
    Restarts the Selenium WebDriver by quitting the current session
    and setting up a new one with a random user agent.

    @param driver: The existing instance of the Selenium WebDriver to be restarted.
    @return: A new instance of the Selenium WebDriver configured with a random user agent.
    """
    driver.quit()
    new_driver = setup_driver()  # Start the drive again with a new random agent
    return new_driver


def get_encoded_search_url(base_url: str, product_name: str) -> str:
    """
    Encodes the product/sku name into a URL-friendly format and constructs the search URL.
    This encoding converts invalid URL characters into a transmittable format over the internet.
    E.g., spaces become + or %20, and special characters are percent-encoded.

    @param base_url: The base URL for the search.
    @param product_name: The name of the product/sku to search for.
    @return: The full search URL.
    """
    encoded_sku = urllib.parse.quote_plus(product_name)  # Encode the product/sku name
    full_url = base_url + encoded_sku  # Combine the base URL and the encoded product/sku name
    return full_url


async def translate_texts_to_english(texts: List[str] | str) -> List[str]:
    """
    Translates a list of product texts to English.

    @param texts: A list of texts in their original language.
    @return: A list of product titles translated to English.
    """
    translator = Translator()
    translated_titles = []
    for title in texts:
        try:
            time.sleep(1)  # Google Translate allows 5 calls/second
            translation = await translator.translate(title, src='auto', dest='en')
            translated_titles.append(translation.text)
        except Exception as e:
            print(f"Translation failed for title: {title}. Error: {e}")
    return translated_titles


def get_best_match_index(search_term: str, translated_titles) -> int:
    """
    Finds the index of the best matching title for a given search term.

    @param search_term: The search term to match against product titles.
    @param translated_titles: A list of translated product titles.
    @return: The index of the best matching title.
    """
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # Load pre-trained model for text similarity
    search_embedding = model.encode(search_term, convert_to_tensor=True)
    product_embeddings = model.encode(translated_titles, convert_to_tensor=True)  # Compute cosine similarities
    similarities = util.pytorch_cos_sim(search_embedding, product_embeddings)
    best_match_index = similarities.argmax().item()  # Get index of best match
    return best_match_index


async def get_best_matching_product(driver: webdriver.Chrome, sku_number: str, sku_name: str,
                                    sku_order_record_id: int) -> Product:
    """
    Finds the product from the search results that matches most with the given SKU name.

    @param driver: The Selenium WebDriver.
    @param sku_number: The SKU number of the product.
    @param sku_name: The SKU name of the product.
    @param sku_order_record_id: unique ERP's id table
    @return: A Product object with details of the best matching product.
    """
    final_search_url = get_encoded_search_url("https://www.skroutz.gr/search?keyphrase=", sku_name)
    driver.get(final_search_url)  # Generate the appropriate search URL using the SKU name
    time.sleep(10)  # Wait to load the page fully
    # Initializations
    product_titles = []
    product_urls = []
    try:
        # Find all product elements that have reviews (filter out the ones without reviews)
        review_products = driver.find_elements(
            By.CSS_SELECTOR, 'div.rating-with-count.react-component:not(.no-sku-reviews)')
        # Locate the closest ancestor <li> element (in the hierarchy) that contains the product details
        product_containers = [p.find_element(By.XPATH, './ancestor::li') for p in review_products]
        # Filters out product elements that do NOT contain an anchor with class 'a.js-sku-link'
        filtered_product_containers = [c for c in product_containers if
                                       c.find_elements(By.CSS_SELECTOR, 'a.js-sku-link')]
        # Within this <a.js-sku-link> element, locate the 'href' and 'title'
        for container in filtered_product_containers:
            product_anchor = container.find_element(By.CSS_SELECTOR, 'a.js-sku-link')
            product_url = product_anchor.get_attribute('href')
            product_title = product_anchor.get_attribute('title')
            if product_url and product_title:
                product_titles.append(product_title)
                product_urls.append(product_url)
        # If indeed the product titles were found, translate them to English and find the best match
        if len(product_titles) > 1:
            translated_titles = await translate_texts_to_english(product_titles)
            best_match_index = get_best_match_index(sku_name, translated_titles)
            best_product = Product(sku_number, sku_name, final_search_url,
                                   product_titles[best_match_index], product_urls[best_match_index],
                                   sku_order_record_id)
            return best_product
        elif len(product_titles) == 1:
            best_product = Product(sku_number, sku_name, final_search_url,
                                   product_titles[0], product_urls[0], sku_order_record_id)
            return best_product
        else:
            print(f"get_best_matching_product(): No search results for SKU: {sku_name}")
    except Exception as e:
        print(f"get_best_matching_product(): Error retrieving product reviews for SKU: {sku_name}\n{e}")
    # If no product found, return a Product with empty 'Product URL' and 'Product title' column
    return Product(sku_number, sku_name, final_search_url, sku_order_record_id=sku_order_record_id)
