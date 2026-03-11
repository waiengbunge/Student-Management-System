from rest_framework import viewsets
from apps.accounts.drf_permissions import RolePermissionDRF

from .models import (
    AttendancePolicy,
    AttendanceSession,
    StudentAttendanceRecord,
    AttendanceAdjustment,
    AttendanceSummary,
    AttendanceWarning,
)
from .serializers import (
    AttendancePolicySerializer,
    AttendanceSessionSerializer,
    StudentAttendanceRecordSerializer,
    AttendanceAdjustmentSerializer,
    AttendanceSummarySerializer,
    AttendanceWarningSerializer,
)


class AttendancePolicyViewSet(viewsets.ModelViewSet):
    queryset = AttendancePolicy.objects.all()
    serializer_class = AttendancePolicySerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'attendance.manage'


class AttendanceSessionViewSet(viewsets.ModelViewSet):
    queryset = AttendanceSession.objects.all()
    serializer_class = AttendanceSessionSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'attendance.manage'


class StudentAttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = StudentAttendanceRecord.objects.all()
    serializer_class = StudentAttendanceRecordSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'attendance.manage'


class AttendanceAdjustmentViewSet(viewsets.ModelViewSet):
    queryset = AttendanceAdjustment.objects.all()
    serializer_class = AttendanceAdjustmentSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'attendance.manage'


class AttendanceSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AttendanceSummary.objects.all()
    serializer_class = AttendanceSummarySerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'attendance.view'


class AttendanceWarningViewSet(viewsets.ModelViewSet):
    queryset = AttendanceWarning.objects.all()
    serializer_class = AttendanceWarningSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'attendance.manage'
