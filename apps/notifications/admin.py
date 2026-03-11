from django.contrib import admin
from .models import (
    NotificationType, Notification, NotificationLog
)

@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "tenant")
    search_fields = ("name", "code")
    list_filter = ("is_active",)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("notification_type", "recipient_user", "recipient_group", "subject", "status", "sent_at", "read_at")
    search_fields = ("subject", "recipient_user__username", "recipient_group")
    list_filter = ("status", "notification_type")

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("notification", "status", "created_at")
    search_fields = ("log_message",)
    list_filter = ("status",)
