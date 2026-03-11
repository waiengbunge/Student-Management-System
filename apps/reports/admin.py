from django.contrib import admin
from .models import (
    ReportTemplate, ReportGenerationRequest, StudentReport, AnalyticsDashboard, DashboardAccess
)

@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "tenant")
    search_fields = ("name", "code")
    list_filter = ("is_active",)

@admin.register(ReportGenerationRequest)
class ReportGenerationRequestAdmin(admin.ModelAdmin):
    list_display = ("template", "requested_by", "status", "started_at", "completed_at")
    search_fields = ("template__name", "requested_by__username")
    list_filter = ("status",)

@admin.register(StudentReport)
class StudentReportAdmin(admin.ModelAdmin):
    list_display = ("student_profile", "report_template", "generated_at", "generated_by")
    search_fields = ("student_profile__student_id",)
    list_filter = ("report_template",)

@admin.register(AnalyticsDashboard)
class AnalyticsDashboardAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "tenant")
    search_fields = ("name", "code")
    list_filter = ("is_active",)

@admin.register(DashboardAccess)
class DashboardAccessAdmin(admin.ModelAdmin):
    list_display = ("dashboard", "user", "access_level", "granted_at")
    search_fields = ("dashboard__name", "user__username")
    list_filter = ("access_level",)
