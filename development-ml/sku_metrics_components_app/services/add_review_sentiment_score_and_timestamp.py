"""
/*
 * Copyright 2024 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from datetime import datetime
from typing import List

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from models.dto_models import Product, Review
from models.models import SkuMetric
from repositories.sku_metric_repository import SkuMetricRepository
from services.web_scraping import products_reviews_scraping
from services.web_scraping.shared import translate_texts_to_english
from utils.database_connection import AsyncSessionLocal


def analyze_sentiment(review: str) -> float:
    """
    Analyze sentiment using VADER.

    @params review: str The text to analyze.
    @return: float The compound sentiment score (range -1 to +1).
    """

    # Create an instance of the SentimentIntensityAnalyzer
    vader_analyzer = SentimentIntensityAnalyzer()
    # Use the analyzer to calculate the sentiment scores for the review
    sentiment_score = vader_analyzer.polarity_scores(review)
    # Extract the compound score, which is a normalized score between -1 (very negative) and +1 (very positive)
    compound_score = sentiment_score['compound']
    # Return
    return compound_score


def stars_to_sentiment(stars: int) -> float:
    """
    Convert star ratings to a simpler sentiment score.

    @params stars: int The star rating.
    @return: float +1 for positive, 0 for neutral, -1 for negative.
    """
    if stars >= 4:
        return 1.0  # Positive sentiment
    elif stars == 3:
        return 0.0  # Neutral sentiment
    else:
        return -1.0  # Negative sentiment


def classify_sentiment(avg_score: float) -> str:
    """
    Classify the overall sentiment for each product.

    @params avg_score: float The average sentiment score.
    @return: str 'Good', 'Bad', or 'Medium' classification.
    """
    if avg_score >= 0.25:
        return 'Good'
    elif avg_score < 0:
        return 'Bad'
    else:
        return 'Medium'


async def process_reviews_sentiment_score_and_timestamp(session: AsyncSession, reviews_data: List[dict]) -> None:
    """
    Process the reviews data, compute sentiment, and update DB with
    `review_sentiment_score` and `review_sentiment_timestamp`.

    @params session: AsyncSession
        The async DB session for updating sku_metric.
    @params reviews_data: List[dict]
        A list of dictionaries representing scraped reviews.
    """
    # Convert to a DataFrame for grouping reviews by "sku_order_record_id"
    df = pd.DataFrame(reviews_data)
    if df.empty:
        print("No reviews data found to process sentiment.")
        return
    grouped = df.groupby("sku_order_record_id")
    # Iterate through each product group
    for sku_order_record_id, group in grouped:
        scores = []
        # Iterate each product's reviews
        for _, row in group.iterrows():
            comments = [
                row['comment'] or '',
                row['pros'] or '',
                row['medium'] or '',
                row['bad'] or '',
                row['no_opinion'] or '',
            ]
            stars = row['stars'] if not pd.isna(row['stars']) else None
            # Translate and analyze sentiment for each comment
            for comment in comments:
                if comment:
                    translated_comment = await translate_texts_to_english(comment)
                    score = analyze_sentiment(translated_comment[0])  # Sentiment score for the comment
                    scores.append(score)
            # Convert star rating to sentiment score and append
            if stars is not None:
                star_score = stars_to_sentiment(int(stars))
                scores.append(star_score)
        # Classify the overall sentiment for the product ('Good', 'Bad', 'Medium')
        if scores and len(scores) > 0:
            avg_score = sum(scores) / len(scores)
            sentiment = classify_sentiment(avg_score)
        else:
            avg_score = None
            sentiment = None
        # Build a SkuMetric object to update
        metric_update = SkuMetric(
            sku_order_record_id=sku_order_record_id,
            review_sentiment_score=avg_score,
            review_sentiment_timestamp=datetime.now(),
        )
        # Update the DB
        sku_metric_repo = SkuMetricRepository(session)
        await sku_metric_repo.update_sku_metric_review_sentiment_score_and_timestamp(metric_update)

    print("Sentiment analysis updates completed.")


async def main(erp_sku_order_development_data: list):
    """
    Main function to:
    1) Collect the scraped reviews by calling `product_reviews_scraping.py`.
    2) Calculate sentiment for each product's reviews.
    3) Update `review_sentiment_score` & `review_sentiment_timestamp` in DB.

    @params erp_sku_order_development_data: list
        The ERP data for filtering records or matching SKUs. Possibly needed
        to filter or identify which SKUs to scrape.
    """
    try:
        async with AsyncSessionLocal() as session:
            # Step 1. Collect fresh product reviews
            scraped_reviews = await products_reviews_scraping.main(erp_sku_order_development_data)
            # TODO: Delete next code line after testing
            # scraped_reviews = _get_scraped_reviews_mocks()
            if not scraped_reviews:
                print("No reviews scraped. Skipping sentiment analysis.")
                return
            # Step 2: Convert list of Review objects to list of dicts
            reviews_data = []
            for rev in scraped_reviews:
                reviews_data.append({
                    "sku_order_record_id": rev.sku_order_record_id,
                    "sku_name": rev.sku_name,
                    "stars": rev.stars,
                    "comment": rev.comment,
                    "pros": ", ".join(rev.pros) if rev.pros else "",
                    "medium": ", ".join(rev.medium) if rev.medium else "",
                    "bad": ", ".join(rev.bad) if rev.bad else "",
                    "no_opinion": ", ".join(rev.no_opinion) if rev.no_opinion else "",
                })
            # Step 3: Process sentiment & update DB
            await process_reviews_sentiment_score_and_timestamp(session, reviews_data)

    except Exception as e:
        print(f"Error in add_review_sentiment_score_and_timestamp main: {e}")
        raise


def _get_scraped_reviews_mocks():
    product_instance = Product(
        sku_number=690323,
        sku_name="Oral-B iO Series 3 Ηλεκτρική Οδοντόβουρτσα Black",
        product_title="Oral-B iO Series 3 Ηλεκτρική Οδοντόβουρτσα",
        sku_order_record_id=1
    )
    scraped_reviews = [
        Review(
            product=product_instance,
            stars='5',
            comment="Εδώ και 9 χρόνια είχα απόλετερα μοντέλα Oral b, η αλήθεια είναι πως η διαφορά είναι τεράστια...\nΔεν χρειάζεστε να πάτε σε...",
            pros=["Αποτελεσματικότητα", "Ευκολία χρήσης", "Ευκολία εύρεσης ανταλλακτικών",
                  "Αυτονομία μπαταρίας", "Σχέση ποιότητας-τιμής"],
            medium=[],
            bad=[],
            no_opinion=[]
        ),
        Review(
            product=product_instance,
            stars='3',
            comment="Η απόδοση είναι καλή, αλλά η τιμή είναι υπερβολική για αυτό που προσφέρει.",
            pros=["Καλή απόδοση"],
            medium=["Υψηλή τιμή", "Κάποιες φορές θορυβώδης"],
            bad=["Πολύ ακριβή"],
            no_opinion=["Εμφάνιση"]
        ),
        Review(
            product=product_instance,
            stars='4',
            comment="Η μπαταρία διαρκεί αρκετά, αλλά η οδοντόβουρτσα είναι λίγο βαριά στο χέρι.",
            pros=[],
            medium=["Βάρος συσκευής"],
            bad=[],
            no_opinion=[]
        ),
        Review(
            product=product_instance,
            stars='2',
            comment="Η τιμή είναι υπερβολική για αυτό που προσφέρει.",
            pros=[],
            medium=[],
            bad=["Πολύ ακριβή"],
            no_opinion=[]
        ),
        Review(
            product=product_instance,
            stars='5',
            comment="",
            pros=[],
            medium=[],
            bad=[],
            no_opinion=[]
        )
    ]
    return scraped_reviews
