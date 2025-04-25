"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: EKETA (CERTH) - Ι.ΜΕΤ. (HIT)
 * Contributor: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod
from typing import Dict


class InventoryServiceInterface(ABC):

    @abstractmethod
    def optimize_inventory(self, params: Dict) -> Dict:
        pass
