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
    # API Configuration
    API_USERNAME: str
    API_PASSWORD: str
    API_PORT: int
    API_HOST: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    CLIENT_DEVELOPMENT_USER_ID: int
    # Database Configuration
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    @property
    def sqlalchemy_database_url(self) -> str:
        """
        Constructs the SQLAlchemy database connection URL.
        """
        return f"mysql+asyncmy://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        # Automatically load variables from .env
        env_file = ".env"


# Global Initialization
settings = Settings()
