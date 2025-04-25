"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.utils.database_session_manager import db_manager
from api.utils.exception_handlers import add_global_exception_handlers
from api.utils.routes import api_router as controllers_routes
from api.utils.settings import settings

# Initialize the FastAPI app
app = FastAPI()

# Register exception handlers
add_global_exception_handlers(app)


async def startup():
    # Begin the database session manager which sets up the database engine and session maker
    db_manager.start_engine()


async def shutdown():
    # Properly close the database connection
    await db_manager.close_engine()


# Register events
app.add_event_handler("startup", startup)  # startup db
app.add_event_handler("shutdown", shutdown)  # shutdown db

# Include routers from controllers
app.include_router(controllers_routes)

# Configure CORS
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Main entry point for running the application/server with Uvicorn
if __name__ == "__main__":
    try:
        uvicorn.run(app, host=settings.DB_HOST, port=settings.API_PORT)
    except BaseException as e:
        print("The server was terminated")
        print("Error:" + str(e))
