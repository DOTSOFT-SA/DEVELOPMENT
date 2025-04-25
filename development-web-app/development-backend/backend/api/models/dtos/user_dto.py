"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class RegisterUserDto:
    email: str
    password: str
    role: str
    privilege_names: List[str]  # List of privilege names provided by the frontend
    code: Optional[str] = None  # Optional - Registration code when add admin users


@dataclass
class UserDto:
    id: int
    email: str
    role: str
    is_active: bool
    updated_at: Optional[datetime]  # Optional because it can be null at some point
    created_at: Optional[datetime]
    login_at: Optional[datetime]
    privilege_names: List[str]
