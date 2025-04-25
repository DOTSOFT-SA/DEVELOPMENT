from django.db import models
from secured_fields.fields import EncryptedCharField

from .login_user import LoginUser


class UserErpApi(models.Model):
    """
    Represents the ERP API links for a specific user.
    Each user has a unique ERP API configuration defining their API endpoints.
    """

    id = models.AutoField(primary_key=True)
    client_name = models.CharField(unique=True, null=False, max_length=255)
    login_token_url = models.TextField(null=False)
    sku_order_url = models.TextField(null=False)
    inventory_params_url = models.TextField(null=True)
    distribution_routing_url = models.TextField(null=True)
    sku_order_latest_url = models.TextField(null=True)
    inventory_params_latest_url = models.TextField(null=True)
    token_username = models.CharField(null=False)
    # Use EncryptedCharField for secure storage of sensitive data
    token_password = EncryptedCharField(null=False, searchable=False)

    # 1-to-1 relationship with LoginUser
    user = models.OneToOneField(
        LoginUser,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name="user_erp_api",
        unique=True
    )

    class Meta:
        db_table = "user_erp_api"

    def __str__(self):
        return f"ERP API Config for {self.client_name} (User ID: {self.user.id})"
