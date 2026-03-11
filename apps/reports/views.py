from rest_framework import viewsets
from apps.accounts.drf_permissions import RolePermissionDRF

from .models import (
    ReportTemplate,
    ReportGenerationRequest,
    StudentReport,
    AnalyticsDashboard,
    DashboardAccess,
)
from .serializers import (
    ReportTemplateSerializer,
    ReportGenerationRequestSerializer,
    StudentReportSerializer,
    AnalyticsDashboardSerializer,
    DashboardAccessSerializer,
)


class ReportTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'reports.manage'


class ReportGenerationRequestViewSet(viewsets.ModelViewSet):
    queryset = ReportGenerationRequest.objects.all()
    serializer_class = ReportGenerationRequestSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'reports.manage'


class StudentReportViewSet(viewsets.ModelViewSet):
    queryset = StudentReport.objects.all()
    serializer_class = StudentReportSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'reports.view'


class AnalyticsDashboardViewSet(viewsets.ModelViewSet):
    queryset = AnalyticsDashboard.objects.all()
    serializer_class = AnalyticsDashboardSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'reports.view'


class DashboardAccessViewSet(viewsets.ModelViewSet):
    queryset = DashboardAccess.objects.all()
    serializer_class = DashboardAccessSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'reports.manage'
