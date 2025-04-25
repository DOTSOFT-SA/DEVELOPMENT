"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class LoginUserManager(BaseUserManager):
    """
    Custom manager for the LoginUser model.
    Provides helper methods to create users with hashed passwords.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email, password, and role.

        @param email: The user's email address.
        @param password: The user's password (hashed automatically).
        @param extra_fields: Additional fields for the user model.
        @return: LoginUser - The created user instance.
        """
        if not email:
            raise ValueError("Email must be provided.")
        email = self.normalize_email(email)  # validate/format the input e-mail appropriately
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Password is hashed and stored securely
        user.save(using=self._db)  # Django's BaseUserManager auto-connects with the _db declared in settings
        return user


class LoginUser(AbstractBaseUser):
    """
    Custom user model that uses email as the unique identifier.
    Maps directly to the 'login_user' table (id, email, password, role, updated_at, created_at).
    """

    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    login_at = models.DateTimeField(null=True, blank=True)

    # Disable the default 'last_login' field from AbstractBaseUser
    last_login = None
    # The above manager now knows that when create a user, the above fields are used
    objects = LoginUserManager()
    # Define 'email' as default username
    USERNAME_FIELD = 'email'

    class Meta:
        db_table = 'login_user'  # Explicitly specify the table name

    def __str__(self):
        """
        @return: str - String representation of this user.
        """
        return f"{self.email}", self.role
