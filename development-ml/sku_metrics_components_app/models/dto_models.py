"""
/*
 * Copyright 2024 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""


# ------------------------
# Models for Web Scraping
# ------------------------

class Product:
    def __init__(self, sku_number, sku_name, sku_search_url=None, product_title=None, product_url=None,
                 sku_order_record_id=None):
        self.sku_number = sku_number
        self.sku_name = sku_name
        self.sku_search_url = sku_search_url
        self.product_title = product_title
        self.product_url = product_url
        self.sku_order_record_id = sku_order_record_id

    def to_dict(self):
        return {
            'sku_number': self.sku_number,
            'sku_name': self.sku_name,
            'sku_search_url': self.sku_search_url,
            'product_tile': self.product_title,
            'product_url': self.product_url,
            'sku_order_record_id': self.sku_order_record_id
        }


class Review:
    def __init__(self, product: Product, stars, comment, pros, medium, bad, no_opinion):
        self.sku_number = product.sku_number
        self.sku_name = product.sku_name
        self.product_title = product.product_title
        self.sku_order_record_id = product.sku_order_record_id
        self.stars = stars
        self.comment = comment
        self.pros = pros
        self.medium = medium
        self.bad = bad
        self.no_opinion = no_opinion

    def to_dict(self):
        return {
            'sku_number': self.sku_number,
            'sku_name': self.sku_name,
            'product_title': self.product_title,
            'sku_order_record_id': self.sku_order_record_id,
            'stars': self.stars,
            'comment': self.comment,
            'pros': self.pros,
            'medium': self.medium,
            'bad': self.bad,
            'no_opinion': self.no_opinion,
        }


class Price:
    def __init__(self, sku_number, sku_name, product_title, prices, average_price):
        self.sku_number = sku_number
        self.sku_name = sku_name
        self.product_title = product_title
        self.prices = prices
        self.average_price = average_price

    def to_dict(self):
        return {
            'su_number': self.sku_number,
            'sku_name': self.sku_name,
            'product_title': self.product_title,
            'prices': self.prices,
            'average_price': self.average_price
        }
