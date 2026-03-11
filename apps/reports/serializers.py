from rest_framework import serializers
from .models import (
    ReportTemplate, ReportGenerationRequest, StudentReport, AnalyticsDashboard, DashboardAccess
)

class ReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = "__all__"

class ReportGenerationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportGenerationRequest
        fields = "__all__"

class StudentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentReport
        fields = "__all__"

class AnalyticsDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsDashboard
        fields = "__all__"

class DashboardAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardAccess
        fields = "__all__"
