"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import os

from dotenv import load_dotenv
from rest_framework import serializers

from ...utils.enums import Role

# Load environment variables
load_dotenv()


class UserSerializer(serializers.Serializer):
    """
    Serializer for the User model, including the majority of fields and its privileges.
    Can be used for various user-related operations like deactivation, updates, etc.
    """
    id = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True)
    role = serializers.CharField(required=True)
    is_active = serializers.BooleanField(default=True)
    updated_at = serializers.DateTimeField(required=True, allow_null=True)
    created_at = serializers.DateTimeField(required=True, allow_null=True)
    login_at = serializers.DateTimeField(required=True, allow_null=True)
    privilege_names = serializers.ListField(
        child=serializers.CharField(), required=True
    )


class RegisterAdminSerializer(serializers.Serializer):
    """
    Serializer for registering a new admin user.
    Ensures that the role of the new user is always 'ADMIN' and validates a registration code.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(required=True)
    privilege_names = serializers.ListField(
        child=serializers.CharField(), required=True
    )
    code = serializers.CharField(write_only=True, required=True)

    @staticmethod
    def validate_role(value):
        """
        Validate that the role is 'ADMIN'.
        """
        if value != Role.ADMIN.value:
            raise serializers.ValidationError(f"The role must be '{Role.ADMIN.value}'.")
        return value

    @staticmethod
    def validate_code(value):
        """
        Validate that the provided code matches the ADMIN_REGISTER_CODE from the .env file.
        """
        admin_register_code = os.getenv("ADMIN_REGISTER_CODE")
        if value != admin_register_code:
            raise serializers.ValidationError
        return value


class RegisterSerializer(serializers.Serializer):
    """
    Serializer for registering a new user.
    Handles validation for RegisterUserDto fields.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(required=True)
    privilege_names = serializers.ListField(
        child=serializers.CharField(), required=True
    )


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class AfterLoginSerializer(serializers.Serializer):
    """
    Serializer for user data after login.
    Handles validation for RegisterUserDto fields and additional timestamps.
    """
    id = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True)
    role = serializers.CharField(required=True)
    login_at = serializers.DateTimeField(required=True, allow_null=True)
    privilege_names = serializers.ListField(
        child=serializers.CharField(), required=True
    )
    is_active = serializers.BooleanField(default=True)


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing the user's password.
    """
    email = serializers.EmailField(required=True)
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)


class ChangePasswordByAdminSerializer(serializers.Serializer):
    """
    Serializer for resting the user's password (only by the Admin).
    """
    email = serializers.EmailField(required=True)
    role = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    code = serializers.CharField(write_only=True, required=True)

    @staticmethod
    def validate_role(value):
        """
        Validate that the role is 'ADMIN'.
        """
        if value != Role.ADMIN.value:
            raise serializers.ValidationError(f"The role must be '{Role.ADMIN.value}'.")
        return value

    @staticmethod
    def validate_code(value):
        """
        Validate that the provided code matches the ADMIN_REGISTER_CODE from the .env file.
        """
        admin_register_code = os.getenv("ADMIN_REGISTER_CODE")
        if value != admin_register_code:
            raise serializers.ValidationError
        return value


class UserErpApiSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    client_name = serializers.CharField(required=True)
    login_token_url = serializers.CharField(required=True)
    sku_order_url = serializers.CharField(required=False, allow_null=True)
    inventory_params_url = serializers.CharField(required=False, allow_null=True)
    distribution_routing_url = serializers.CharField(required=False, allow_null=True)
    sku_order_latest_url = serializers.CharField(required=False, allow_null=True)
    inventory_params_latest_url = serializers.CharField(required=False, allow_null=True)
    token_username = serializers.CharField(required=True)
    token_password = serializers.CharField(required=True)
