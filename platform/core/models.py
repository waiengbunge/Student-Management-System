from django.db import models
from django.conf import settings


class Organization(models.Model):
    ORGANIZATION_TYPES = [
        ('school', 'School'),
        ('company', 'Company'),
        ('hospital', 'Hospital'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=ORGANIZATION_TYPES, default='school')
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



"""
This module previously defined local `Role`, `Permission`, and `AuditLog` models which
duplicated definitions found in `apps.accounts.models` and `apps.common.models`.

To avoid DB table conflicts and keep a single source-of-truth, alias the canonical
models from the relevant apps. Keep `Organization` and `Notification` here.
"""

from apps.accounts import models as accounts_models
from apps.common import models as common_models

# Re-export canonical RBAC / audit models to avoid duplicate DB tables.
Role = accounts_models.Role
Permission = accounts_models.Permission
AuditLog = common_models.AuditLog


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='notifications')

    def __str__(self):
        return self.title