"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse


def add_global_exception_handlers(app: FastAPI):
    """
    Registers global exception handlers to the FastAPI app.
    """

    # Catch all unexpected exceptions
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """
        Handles all unexpected exceptions globally.
        """
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred on our side.",
                "error": str(exc),
            },
        )
