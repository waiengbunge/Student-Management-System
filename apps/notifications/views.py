from rest_framework import viewsets
from apps.accounts.drf_permissions import RolePermissionDRF

from .models import NotificationType, Notification, NotificationLog
from .serializers import (
    NotificationTypeSerializer,
    NotificationSerializer,
    NotificationLogSerializer,
)


class NotificationTypeViewSet(viewsets.ModelViewSet):
    queryset = NotificationType.objects.all()
    serializer_class = NotificationTypeSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'notifications.view',
        'retrieve': 'notifications.view',
        'create': 'notifications.manage',
        'update': 'notifications.manage',
        'partial_update': 'notifications.manage',
        'destroy': 'notifications.manage',
    }

    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'notifications.view',
        'retrieve': 'notifications.view',
        'create': 'notifications.manage',
        'update': 'notifications.manage',
        'partial_update': 'notifications.manage',
        'destroy': 'notifications.manage',
    }

    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)


class NotificationLogViewSet(viewsets.ModelViewSet):
    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer
    permission_classes = [RolePermissionDRF]
    required_permission_map = {
        'list': 'notifications.view',
        'retrieve': 'notifications.view',
        'create': 'notifications.manage',
        'update': 'notifications.manage',
        'partial_update': 'notifications.manage',
        'destroy': 'notifications.manage',
    }

    def get_required_permission(self, request):
        return self.required_permission_map.get(self.action)
