from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ReportTemplateViewSet,
    ReportGenerationRequestViewSet,
    StudentReportViewSet,
    AnalyticsDashboardViewSet,
    DashboardAccessViewSet,
)

router = DefaultRouter()
router.register(r"templates", ReportTemplateViewSet)
router.register(r"generation-requests", ReportGenerationRequestViewSet)
router.register(r"student-reports", StudentReportViewSet)
router.register(r"dashboards", AnalyticsDashboardViewSet)
router.register(r"dashboard-access", DashboardAccessViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
