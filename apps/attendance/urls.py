from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AttendancePolicyViewSet,
    AttendanceSessionViewSet,
    StudentAttendanceRecordViewSet,
    AttendanceAdjustmentViewSet,
    AttendanceSummaryViewSet,
    AttendanceWarningViewSet,
)

router = DefaultRouter()
router.register(r"policies", AttendancePolicyViewSet)
router.register(r"sessions", AttendanceSessionViewSet)
router.register(r"records", StudentAttendanceRecordViewSet)
router.register(r"adjustments", AttendanceAdjustmentViewSet)
router.register(r"summaries", AttendanceSummaryViewSet)
router.register(r"warnings", AttendanceWarningViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
