"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""
import json
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

''' This file is responsible for loading the configurations from the .env file '''

# Load the .env file
load_dotenv()


class Settings(BaseSettings):
    # Database Configuration
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    api_host: str
    api_port: str
    api_register_admin_url: str
    api_register_user_url: str
    api_register_erp_api_url: str
    api_login_admin_url: str
    admin_email: str
    admin_password: str

    class Config:
        # Automatically load variables from .env
        env_file = ".env"


# Global Initialization
settings = Settings()

# Load default users from users.json
root_path = os.path.dirname(os.path.dirname(__file__))
config_file_path = os.path.join(root_path, "configs", "users.json")
try:
    with open(config_file_path, "r", encoding="utf-8") as f:
        api_clients_configs = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"Configuration file not found at {config_file_path}")
except json.JSONDecodeError as e:
    raise ValueError("Invalid JSON format in users.json") from e

# Load ERP API configurations from users_erp_api.json
erp_api_config_file_path = os.path.join(root_path, "configs", "users_erp_api.json")
try:
    with open(erp_api_config_file_path, "r", encoding="utf-8") as f:
        api_users_erp_api_configs = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"ERP API configuration file not found at {erp_api_config_file_path}")
except json.JSONDecodeError as e:
    raise ValueError("Invalid JSON format in users_erp_api.json") from e
