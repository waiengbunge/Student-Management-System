from rest_framework import viewsets, filters
from apps.students.models import StudentProfile, GuardianProfile, Enrollment
from .serializers import StudentProfileSerializer, GuardianProfileSerializer, EnrollmentSerializer
from apps.accounts.drf_permissions import RolePermissionDRF
from apps.api.pagination import StandardResultsSetPagination


class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'students.profile.view',
        'retrieve': 'students.profile.view',
        'create': 'students.profile.create',
        'update': 'students.profile.update',
        'partial_update': 'students.profile.update',
        'destroy': 'students.profile.delete',
    }

    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student_number', 'user__email']
    ordering_fields = ['student_number', 'admitted_on']

    def get_queryset(self):
        qs = StudentProfile.objects.all()
        if self.request and not getattr(self.request.user, 'is_superuser', False):
            tenant = getattr(self.request.user, 'tenant', None)
            if tenant is not None:
                qs = qs.filter(tenant=tenant)
        return qs


class GuardianProfileViewSet(viewsets.ModelViewSet):
    queryset = GuardianProfile.objects.all()
    serializer_class = GuardianProfileSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'students.guardian.view',
        'retrieve': 'students.guardian.view',
        'create': 'students.guardian.create',
        'update': 'students.guardian.update',
        'partial_update': 'students.guardian.update',
        'destroy': 'students.guardian.delete',
    }

    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'email', 'phone']
    ordering_fields = ['full_name']

    def get_queryset(self):
        qs = GuardianProfile.objects.all()
        if self.request and not getattr(self.request.user, 'is_superuser', False):
            tenant = getattr(self.request.user, 'tenant', None)
            if tenant is not None:
                qs = qs.filter(user__tenant=tenant)
        return qs


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'students.enrollment.view',
        'retrieve': 'students.enrollment.view',
        'create': 'students.enrollment.create',
        'update': 'students.enrollment.update',
        'partial_update': 'students.enrollment.update',
        'destroy': 'students.enrollment.delete',
    }

    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['enrollment_number', 'student_profile__student_number']
    ordering_fields = ['enrolled_on', 'enrollment_number']

    def get_queryset(self):
        qs = Enrollment.objects.select_related('student_profile', 'program').all()
        if self.request and not getattr(self.request.user, 'is_superuser', False):
            tenant = getattr(self.request.user, 'tenant', None)
            if tenant is not None:
                qs = qs.filter(student_profile__tenant=tenant)
        return qs
