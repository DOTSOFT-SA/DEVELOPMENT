"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

''' This file is responsible for loading the configurations from the .env file '''

# Load the .env file
load_dotenv()


class Settings(BaseSettings):
    # Database Configuration
    db_username_super: str
    db_password_super: str
    db_username: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    class Config:
        # Automatically load variables from .env
        env_file = ".env"


# Global Initialization
settings = Settings()
