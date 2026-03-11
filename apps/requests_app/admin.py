from django.contrib import admin
from .models import (
    RequestType, Request, RequestComment, RequestAttachment
)

@admin.register(RequestType)
class RequestTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "tenant")
    search_fields = ("name", "code")
    list_filter = ("is_active",)

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ("request_type", "requested_by", "subject", "status", "created_at", "closed_at")
    search_fields = ("subject", "requested_by__username")
    list_filter = ("status", "request_type")

@admin.register(RequestComment)
class RequestCommentAdmin(admin.ModelAdmin):
    list_display = ("request", "commented_by", "created_at")
    search_fields = ("comment", "commented_by__username")
    list_filter = ("created_at",)

@admin.register(RequestAttachment)
class RequestAttachmentAdmin(admin.ModelAdmin):
    list_display = ("request", "uploaded_by", "uploaded_at")
    search_fields = ("uploaded_by__username",)
    list_filter = ("uploaded_at",)
