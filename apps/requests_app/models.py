from django.db import models
from apps.common.models import TenantScopedModel, TimeStampedModel

class RequestType(TenantScopedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = "request_types"
        unique_together = [("tenant", "code")]

class Request(TimeStampedModel):
    request_type = models.ForeignKey("requests_app.RequestType", on_delete=models.PROTECT)
    requested_by = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.SET_NULL, null=True, blank=True)
    staff_profile = models.ForeignKey("hr.StaffProfile", on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=30, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "requests"

class RequestComment(TimeStampedModel):
    request = models.ForeignKey("requests_app.Request", on_delete=models.CASCADE, related_name="comments")
    commented_by = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "request_comments"

class RequestAttachment(TimeStampedModel):
    request = models.ForeignKey("requests_app.Request", on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="request_attachments/")
    uploaded_by = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "request_attachments"
