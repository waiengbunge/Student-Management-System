from django.db import models
from django.conf import settings
from django.utils import timezone

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        abstract = True
    @property
    def is_deleted(self):
        return self.deleted_at is not None
    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

class TenantScopedModel(TimeStampedModel, SoftDeleteModel):
    tenant = models.ForeignKey(
        "saas.Tenant",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)ss",
    )
    class Meta:
        abstract = True

class CampusScopedModel(TenantScopedModel):
    campus = models.ForeignKey(
        "saas.Campus",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)ss",
    )
    class Meta:
        abstract = True

class UserStampedModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_%(app_label)s_%(class)ss",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_%(app_label)s_%(class)ss",
    )
    class Meta:
        abstract = True

class FileUpload(TimeStampedModel):
    tenant = models.ForeignKey("saas.Tenant", on_delete=models.CASCADE, related_name="file_uploads")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    disk = models.CharField(max_length=50, default="default")
    path = models.CharField(max_length=500)
    original_name = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=120, blank=True)
    file_size = models.BigIntegerField(default=0)
    checksum = models.CharField(max_length=255, blank=True)
    visibility = models.CharField(max_length=20, default="private")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "file_uploads"

class ActivityLog(TimeStampedModel):
    tenant = models.ForeignKey("saas.Tenant", on_delete=models.CASCADE, related_name="activity_logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    module = models.CharField(max_length=120)
    action = models.CharField(max_length=120)
    entity_type = models.CharField(max_length=120)
    entity_id = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    class Meta:
        db_table = "activity_logs"

class AuditLog(TimeStampedModel):
    tenant = models.ForeignKey("saas.Tenant", on_delete=models.CASCADE, related_name="audit_logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    table_name = models.CharField(max_length=120)
    record_pk = models.CharField(max_length=120)
    operation = models.CharField(max_length=20)
    old_values_json = models.JSONField(null=True, blank=True)
    new_values_json = models.JSONField(null=True, blank=True)
    changed_at = models.DateTimeField()
    class Meta:
        db_table = "audit_logs"
