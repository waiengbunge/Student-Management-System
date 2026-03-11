from rest_framework import viewsets, filters
from apps.accounts.models import User, Role, Permission, ApiKey
from .serializers import UserSerializer, RoleSerializer, PermissionSerializer
from .serializers import UserRoleSerializer
from .serializers import ApiKeySerializer
from apps.accounts.drf_permissions import RolePermissionDRF
from apps.api.pagination import StandardResultsSetPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import hashlib


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'accounts.user.view',
        'retrieve': 'accounts.user.view',
        'create': 'accounts.user.create',
        'update': 'accounts.user.update',
        'partial_update': 'accounts.user.update',
        'destroy': 'accounts.user.delete',
    }

    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'phone']
    ordering_fields = ['username', 'email', 'created_at']

    @action(detail=True, methods=['post'], url_path='change-password')
    def change_password(self, request, pk=None):
        user = self.get_object()
        if not request.user.has_perm('accounts.user.update') and not request.user.is_superuser:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        new_password = request.data.get('password')
        if not new_password:
            return Response({'password': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password updated.'})

    def get_queryset(self):
        qs = User.objects.all()
        request = self.request
        if request and not getattr(request.user, 'is_superuser', False):
            tenant = getattr(request.user, 'tenant', None)
            if tenant is not None:
                qs = qs.filter(tenant=tenant)
        return qs


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'accounts.role.view',
        'retrieve': 'accounts.role.view',
        'create': 'accounts.role.create',
        'update': 'accounts.role.update',
        'partial_update': 'accounts.role.update',
        'destroy': 'accounts.role.delete',
    }

    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']

    def get_queryset(self):
        qs = Role.objects.all()
        if self.request and not getattr(self.request.user, 'is_superuser', False):
            tenant = getattr(self.request.user, 'tenant', None)
            if tenant is not None:
                qs = qs.filter(tenant=tenant)
        return qs


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'accounts.permission.view',
        'retrieve': 'accounts.permission.view',
        'create': 'accounts.permission.create',
        'update': 'accounts.permission.update',
        'partial_update': 'accounts.permission.update',
        'destroy': 'accounts.permission.delete',
    }

    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['module', 'action', 'code']
    ordering_fields = ['module', 'action', 'code']

    def get_queryset(self):
        qs = Permission.objects.all()
        if self.request and not getattr(self.request.user, 'is_superuser', False):
            tenant = getattr(self.request.user, 'tenant', None)
            # permissions may be global; but keep safe filter if tenanted
            if tenant is not None:
                qs = qs.filter(rolepermission__role__tenant=tenant).distinct()
        return qs


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'accounts.userrole.view',
        'retrieve': 'accounts.userrole.view',
        'create': 'accounts.userrole.assign',
        'update': 'accounts.userrole.update',
        'partial_update': 'accounts.userrole.update',
        'destroy': 'accounts.userrole.revoke',
    }

    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)

    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__email', 'role__name']
    ordering_fields = ['created_at']

    def get_queryset(self):
        qs = UserRole.objects.select_related('role', 'user').all()
        if self.request and not getattr(self.request.user, 'is_superuser', False):
            tenant = getattr(self.request.user, 'tenant', None)
            if tenant is not None:
                qs = qs.filter(role__tenant=tenant)
        return qs


class ApiKeyViewSet(viewsets.ModelViewSet):
    queryset = ApiKey.objects.all()
    serializer_class = ApiKeySerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'accounts.apikey.view',
        'retrieve': 'accounts.apikey.view',
        'create': 'accounts.apikey.create',
        'destroy': 'accounts.apikey.delete',
    }

    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)

    def perform_destroy(self, instance):
        # zero out hash for safety before deletion audit
        try:
            instance.key_hash = ''
            instance.save()
        except Exception:
            pass
        instance.delete()

    def get_queryset(self):
        qs = ApiKey.objects.all()
        if self.request and not getattr(self.request.user, 'is_superuser', False):
            tenant = getattr(self.request.user, 'tenant', None)
            # restrict to tenant or keys created by the user
            qs = qs.filter(tenant=tenant)
        return qs
