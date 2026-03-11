from rest_framework import viewsets, filters
from apps.accounts.drf_permissions import RolePermissionDRF
from .models import Exam, ExamSchedule, StudentExamResult
from .serializers import ExamSerializer, ExamScheduleSerializer, StudentExamResultSerializer
from apps.api.pagination import StandardResultsSetPagination
from rest_framework.decorators import action
from rest_framework.response import Response


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'exams.manage'
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'course__name']

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        exam = self.get_object()
        exam.is_published = True
        exam.save()
        return Response({'published': True})


class ExamScheduleViewSet(viewsets.ModelViewSet):
    queryset = ExamSchedule.objects.all()
    serializer_class = ExamScheduleSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'exams.manage'


class StudentExamResultViewSet(viewsets.ModelViewSet):
    queryset = StudentExamResult.objects.all()
    serializer_class = StudentExamResultSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'exams.view',
        'retrieve': 'exams.view',
        'create': 'exams.manage',
        'update': 'exams.manage',
        'partial_update': 'exams.manage',
        'destroy': 'exams.manage',
    }

    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)

    @action(detail=True, methods=['post'])
    def compute_grade(self, request, pk=None):
        r = self.get_object()
        score = r.score or 0
        if score >= 85:
            g = 'A'
        elif score >= 70:
            g = 'B'
        elif score >= 50:
            g = 'C'
        else:
            g = 'F'
        r.grade = g
        r.save()
        return Response({'grade': g})
from rest_framework import viewsets
from apps.accounts.drf_permissions import RolePermissionDRF

from .models import (
    ExamType,
    ExamSession,
    ExamPaper,
    ExamSeating,
    ExamAttendance,
    ExamResult,
    ExamResultAdjustment,
)
from .serializers import (
    ExamTypeSerializer,
    ExamSessionSerializer,
    ExamPaperSerializer,
    ExamSeatingSerializer,
    ExamAttendanceSerializer,
    ExamResultSerializer,
    ExamResultAdjustmentSerializer,
)


class ExamTypeViewSet(viewsets.ModelViewSet):
    queryset = ExamType.objects.all()
    serializer_class = ExamTypeSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'exams.manage'


class ExamSessionViewSet(viewsets.ModelViewSet):
    queryset = ExamSession.objects.all()
    serializer_class = ExamSessionSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'exams.manage'


class ExamPaperViewSet(viewsets.ModelViewSet):
    queryset = ExamPaper.objects.all()
    serializer_class = ExamPaperSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'exams.manage'


class ExamSeatingViewSet(viewsets.ModelViewSet):
    queryset = ExamSeating.objects.all()
    serializer_class = ExamSeatingSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'exams.manage'


class ExamAttendanceViewSet(viewsets.ModelViewSet):
    queryset = ExamAttendance.objects.all()
    serializer_class = ExamAttendanceSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'exams.manage'


class ExamResultViewSet(viewsets.ModelViewSet):
    queryset = ExamResult.objects.all()
    serializer_class = ExamResultSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'exams.manage'


class ExamResultAdjustmentViewSet(viewsets.ModelViewSet):
    queryset = ExamResultAdjustment.objects.all()
    serializer_class = ExamResultAdjustmentSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'exams.manage'
