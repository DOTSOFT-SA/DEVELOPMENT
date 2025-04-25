"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import Optional

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from .user_erp_api_repository_interface import UserErpApiRepositoryInterface
from ..models.user_erp_api import UserErpApi
from ..utils.constant_vars import CACHE_EXPIRE_TIME


class UserErpApiRepository(UserErpApiRepositoryInterface):
    """
    Repository for handling database operations related to UserErpApi.
    """

    @staticmethod
    def find_user_erp_api_by_user_id(user_id: int) -> Optional[UserErpApi]:
        """
        Retrieve the ERP API record for the given user_id, with caching to reduce DB lookups.
        If not found in cache, fetch from DB and store in cache.

        :param user_id: int: The ID of the user whose ERP API record we want.
        :return: Optional[UserErpApi]: The ERP API configuration record if found, otherwise None.
        """
        cache_key = f"user_erp_api:{user_id}"
        cached_record = cache.get(cache_key)
        if cached_record:
            return cached_record
        # If not in cache, query the DB
        try:
            record = UserErpApi.objects.filter(user_id=user_id).first()
            if record:
                # Store in cache with expire time
                cache.set(cache_key, record, CACHE_EXPIRE_TIME)
            return record
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def store_or_update_user_erp_api_record(user_erp_api_record: UserErpApi) -> Optional[UserErpApi]:
        """
        Store a new UserErpApi record or update an existing one in the database.
        If a record exists for the given user_id, update the existing record;
        otherwise, create a new one.

        After saving to DB, we also update the cache so subsequent calls to
        (e.g. fetch_erp_api_by_user_id() won't get stale data)

        :param user_erp_api_record: UserErpApi: The record containing the user's ERP API links.
        :return: Optional[UserErpApi]: The newly created or updated record.
        """
        existing_record = UserErpApiRepository.find_user_erp_api_by_user_id(user_erp_api_record.user_id)
        if existing_record:
            # We'll exclude fields that shouldn't be overwritten
            excluded_fields = {"id", "user_id", "_state"}
            # Dynamically copy fields from user_erp_api_record to existing_record
            for field_name, value in user_erp_api_record.__dict__.items():
                if field_name not in excluded_fields:
                    setattr(existing_record, field_name, value)
            existing_record.save()
            # Invalidate or update the cache
            cache_key = f"user_erp_api:{existing_record.user_id}"
            cache.set(cache_key, existing_record, CACHE_EXPIRE_TIME)
            return existing_record
        # If no record exists, create a new one
        user_erp_api_record.save()
        # Update cache with the new record
        cache_key = f"user_erp_api:{user_erp_api_record.user_id}"
        cache.set(cache_key, user_erp_api_record, CACHE_EXPIRE_TIME)
        return user_erp_api_record
