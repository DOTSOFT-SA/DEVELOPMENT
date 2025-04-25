"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod
from typing import Optional


class ErpDevelopmentRepositoryInterface(ABC):

    @abstractmethod
    def fetch_erp_api_token(self, user_id: int) -> Optional[str]:
        pass

    @abstractmethod
    def fetch_data_from_erp(self, url: str, token: str, method: str, payload=None) -> Optional[dict]:
        pass
