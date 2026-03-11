from django.db import models
from apps.common.models import TenantScopedModel, TimeStampedModel

class NotificationType(TenantScopedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = "notification_types"
        unique_together = [("tenant", "code")]

class Notification(TimeStampedModel):
    notification_type = models.ForeignKey("notifications.NotificationType", on_delete=models.PROTECT)
    recipient_user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, null=True, blank=True)
    recipient_group = models.CharField(max_length=120, blank=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=30, default="pending")
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "notifications"

class NotificationLog(TimeStampedModel):
    notification = models.ForeignKey("notifications.Notification", on_delete=models.CASCADE, related_name="logs")
    status = models.CharField(max_length=30)
    log_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "notification_logs"
