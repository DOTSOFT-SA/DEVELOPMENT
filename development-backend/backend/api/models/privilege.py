"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from django.db import models


class Privilege(models.Model):
    """
    Django model corresponding to the 'privilege' table.
    id: Primary key (SERIAL)
    name: VARCHAR(255) UNIQUE NOT NULL
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'privilege'

    def __str__(self):
        """
        @return: str - String representation of the privilege object.
        """
        return f"Privilege: {self.name}"
