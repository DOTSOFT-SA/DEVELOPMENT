"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from rest_framework.exceptions import ValidationError


def force_user_id_as_criteria(request) -> dict:
    """
    Ensures that the 'user_id' parameter is present in the request's query parameters.
    If 'user_id' is missing, an exception is raised.

    @param request: The incoming request object that contains query parameters.
    @return: A modified dictionary of query parameters containing 'user_id'.
    @raises ValueError: If 'user_id' is missing from the request parameters.
    """
    user_id = request.query_params.get("user_id")
    if not user_id:
        raise ValidationError("Parameter 'user_id' is required")
    query_params = request.query_params.copy()  # Fix QueryDict instance is immutable
    query_params["user_id"] = int(user_id)
    return query_params
