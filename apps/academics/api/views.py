from rest_framework import viewsets, filters
from apps.academics.models import Program, Course, Class, ClassLevel, Classroom
from .serializers import ProgramSerializer, CourseSerializer, ClassSerializer, ClassLevelSerializer, ClassroomSerializer
from apps.accounts.drf_permissions import RolePermissionDRF
from apps.api.pagination import StandardResultsSetPagination


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'academics.program.view',
        'retrieve': 'academics.program.view',
        'create': 'academics.program.create',
        'update': 'academics.program.update',
        'partial_update': 'academics.program.update',
        'destroy': 'academics.program.delete',
    }
    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']

    def get_queryset(self):
        qs = Program.objects.all()
        if self.request and not getattr(self.request.user, 'is_superuser', False):
            tenant = getattr(self.request.user, 'tenant', None)
            if tenant is not None:
                qs = qs.filter(tenant=tenant)
        return qs


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'academics.course.view',
        'retrieve': 'academics.course.view',
        'create': 'academics.course.create',
        'update': 'academics.course.update',
        'partial_update': 'academics.course.update',
        'destroy': 'academics.course.delete',
    }
    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']

    def get_queryset(self):
        qs = Course.objects.all()
        if self.request and not getattr(self.request.user, 'is_superuser', False):
            tenant = getattr(self.request.user, 'tenant', None)
            if tenant is not None:
                qs = qs.filter(tenant=tenant)
        return qs


class ClassLevelViewSet(viewsets.ModelViewSet):
    queryset = ClassLevel.objects.all()
    serializer_class = ClassLevelSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'academics.classlevel.view',
        'retrieve': 'academics.classlevel.view',
        'create': 'academics.classlevel.create',
        'update': 'academics.classlevel.update',
        'partial_update': 'academics.classlevel.update',
        'destroy': 'academics.classlevel.delete',
    }
    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'academics.class.view',
        'retrieve': 'academics.class.view',
        'create': 'academics.class.create',
        'update': 'academics.class.update',
        'partial_update': 'academics.class.update',
        'destroy': 'academics.class.delete',
    }
    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']

    def get_queryset(self):
        qs = Class.objects.all()
        if self.request and not getattr(self.request.user, 'is_superuser', False):
            tenant = getattr(self.request.user, 'tenant', None)
            if tenant is not None:
                qs = qs.filter(tenant=tenant)
        return qs


class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'academics.classroom.view',
        'retrieve': 'academics.classroom.view',
        'create': 'academics.classroom.create',
        'update': 'academics.classroom.update',
        'partial_update': 'academics.classroom.update',
        'destroy': 'academics.classroom.delete',
    }
    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']
