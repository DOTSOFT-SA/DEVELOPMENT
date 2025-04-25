"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""


class CustomLoggerException(Exception):
    """
    Custom exception class to handle application-specific errors.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
