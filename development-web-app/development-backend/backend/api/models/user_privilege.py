"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from django.db import models

from ..models.login_user import LoginUser
from ..models.privilege import Privilege


class UserPrivilege(models.Model):
    """
    Django model corresponding to the 'user_privilege' join table.
    id: Primary key (SERIAL)
    is_enabled: BOOLEAN NOT NULL DEFAULT TRUE
    updated_at: TIMESTAMP
    created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    user_id: Foreign key to login_user(id), ON DELETE CASCADE
    privilege_id: Foreign key to privilege(id), ON DELETE CASCADE
    """

    id = models.AutoField(primary_key=True)
    is_enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Foreign keys
    user = models.ForeignKey(
        LoginUser,
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    privilege = models.ForeignKey(
        Privilege,
        on_delete=models.CASCADE,
        db_column='privilege_id'
    )

    class Meta:
        db_table = 'user_privilege'

    def __str__(self):
        """
        @return: str - String representation including related user and privilege.
        """
        return f"UserPrivilege: user({self.user.email}) -> privilege({self.privilege.name})"
