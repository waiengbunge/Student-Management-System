from django.db import models
from apps.common.models import TenantScopedModel, TimeStampedModel

class ReportTemplate(TenantScopedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    template_file = models.FileField(upload_to="report_templates/")
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = "report_templates"
        unique_together = [("tenant", "code")]

class ReportGenerationRequest(TimeStampedModel):
    template = models.ForeignKey("reports.ReportTemplate", on_delete=models.CASCADE)
    requested_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    parameters = models.JSONField()
    status = models.CharField(max_length=30, default="pending")
    generated_file = models.FileField(upload_to="generated_reports/", null=True, blank=True)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "report_generation_requests"

class StudentReport(TimeStampedModel):
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE)
    report_template = models.ForeignKey("reports.ReportTemplate", on_delete=models.SET_NULL, null=True, blank=True)
    generated_file = models.FileField(upload_to="student_reports/", null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    class Meta:
        db_table = "student_reports"

class AnalyticsDashboard(TenantScopedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    config = models.JSONField()
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = "analytics_dashboards"
        unique_together = [("tenant", "code")]

class DashboardAccess(TimeStampedModel):
    dashboard = models.ForeignKey("reports.AnalyticsDashboard", on_delete=models.CASCADE)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    access_level = models.CharField(max_length=30, default="viewer")
    granted_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "dashboard_access"
        unique_together = [("dashboard", "user")]
