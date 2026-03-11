from rest_framework import viewsets, filters
from apps.accounts.drf_permissions import RolePermissionDRF
from .models import Assessment, AssessmentItem, StudentAssessment
from .serializers import AssessmentSerializer, AssessmentItemSerializer, StudentAssessmentSerializer
from apps.api.pagination import StandardResultsSetPagination
from rest_framework.decorators import action
from rest_framework.response import Response


class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'assessments.manage'
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']


class AssessmentItemViewSet(viewsets.ModelViewSet):
    queryset = AssessmentItem.objects.all()
    serializer_class = AssessmentItemSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'assessments.manage'


class StudentAssessmentViewSet(viewsets.ModelViewSet):
    queryset = StudentAssessment.objects.all()
    serializer_class = StudentAssessmentSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'assessments.view',
        'retrieve': 'assessments.view',
        'create': 'assessments.manage',
        'update': 'assessments.manage',
        'partial_update': 'assessments.manage',
        'destroy': 'assessments.manage',
    }

    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)

    @action(detail=True, methods=['post'])
    def compute_grade(self, request, pk=None):
        sa = self.get_object()
        # simple grading: map numeric score -> grade
        score = sa.score or 0
        if score >= 85:
            g = 'A'
        elif score >= 70:
            g = 'B'
        elif score >= 50:
            g = 'C'
        else:
            g = 'F'
        sa.grade = g
        sa.save()
        return Response({'grade': g})
from rest_framework import viewsets
from apps.accounts.drf_permissions import RolePermissionDRF

from .models import (
    GradingScheme,
    GradingSchemeItem,
    AssessmentComponent,
    AssessmentItem,
    StudentAssessment,
    AssessmentAdjustment,
    AssessmentFeedback,
    PassFailRule,
    GradePublicationBatch,
)
from .serializers import (
    GradingSchemeSerializer,
    GradingSchemeItemSerializer,
    AssessmentComponentSerializer,
    AssessmentItemSerializer,
    StudentAssessmentSerializer,
    AssessmentAdjustmentSerializer,
    AssessmentFeedbackSerializer,
    PassFailRuleSerializer,
    GradePublicationBatchSerializer,
)


class GradingSchemeViewSet(viewsets.ModelViewSet):
    queryset = GradingScheme.objects.all()
    serializer_class = GradingSchemeSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'assessments.manage'


class GradingSchemeItemViewSet(viewsets.ModelViewSet):
    queryset = GradingSchemeItem.objects.all()
    serializer_class = GradingSchemeItemSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'assessments.manage'


class AssessmentComponentViewSet(viewsets.ModelViewSet):
    queryset = AssessmentComponent.objects.all()
    serializer_class = AssessmentComponentSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'assessments.manage'


class AssessmentItemViewSet(viewsets.ModelViewSet):
    queryset = AssessmentItem.objects.all()
    serializer_class = AssessmentItemSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'assessments.manage'


class StudentAssessmentViewSet(viewsets.ModelViewSet):
    queryset = StudentAssessment.objects.all()
    serializer_class = StudentAssessmentSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'assessments.manage'


class AssessmentAdjustmentViewSet(viewsets.ModelViewSet):
    queryset = AssessmentAdjustment.objects.all()
    serializer_class = AssessmentAdjustmentSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'assessments.manage'


class AssessmentFeedbackViewSet(viewsets.ModelViewSet):
    queryset = AssessmentFeedback.objects.all()
    serializer_class = AssessmentFeedbackSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'assessments.manage'


class PassFailRuleViewSet(viewsets.ModelViewSet):
    queryset = PassFailRule.objects.all()
    serializer_class = PassFailRuleSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'assessments.manage'


class GradePublicationBatchViewSet(viewsets.ModelViewSet):
    queryset = GradePublicationBatch.objects.all()
    serializer_class = GradePublicationBatchSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'assessments.manage'
