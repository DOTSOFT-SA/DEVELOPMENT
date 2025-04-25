"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from enum import Enum


class Role(Enum):
    ADMIN = "ΔΙΑΧΕΙΡΙΣΤΗΣ"
    USER = "ΧΡΗΣΤΗΣ"

    # Return a list of all the enums/roles belong to the Role class
    @classmethod
    def list_roles(cls):
        return [role.value for role in cls]


class UserPrivileges(Enum):
    ADMIN_PRIVILEGE = "ΔΙΑΧΕΙΡΙΣΤΗΣ"
    DEMAND_FORECASTING = "ΠΡΟΒΛΕΨΗ ΖΗΤΗΣΗΣ"
    RECOMMENDED_STOCK_QUANTITY = "ΣΥΝΙΣΤΩΜΕΝΗ ΠΟΣΟΤΗΤΑ ΑΠΟΘΕΜΑΤΩΝ"
    ROUTING = "ΔΡΟΜΟΛΟΓΗΣΗ"

    # Return a list of all the enums/privileges in the UserPrivilege class
    @classmethod
    def list_privileges(cls):
        return [privilege.value for privilege in cls]


class MLModelName(Enum):
    SKU_ORDER_QUANTITY_PREDICTION_MODEL = "sku_order_quantity_prediction_ml_model"

    # Return a list of all the enums/models in the MLModelType class
    @classmethod
    def list_models(cls):
        return [model.value for model in cls]
