"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from utils.settings import settings

# Load environment variables from .env file
load_dotenv()

# Get database connection info from environment variables
DB_USERNAME_SUPER = settings.db_username_super
DB_PASSWORD_SUPER = settings.db_password_super
DB_USERNAME = settings.db_username
DB_PASSWORD = settings.db_password
DB_HOST = settings.db_host
DB_PORT = settings.db_port
DB_NAME = settings.db_name

# URL-encode credentials
encoded_user = quote_plus(DB_USERNAME)
encoded_pass = quote_plus(DB_PASSWORD)
encoded_user_super = quote_plus(DB_USERNAME_SUPER)
encoded_pass_super = quote_plus(DB_PASSWORD_SUPER)

# Build connection strings safely
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{encoded_user}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
SQLALCHEMY_DATABASE_URL_SUPER = (
    f"mysql+pymysql://{encoded_user_super}:{encoded_pass_super}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
engine_super = create_engine(SQLALCHEMY_DATABASE_URL_SUPER)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
