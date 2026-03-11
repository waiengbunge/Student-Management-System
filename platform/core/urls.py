from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import OrganizationViewSet, RoleViewSet, PermissionViewSet, AuditLogViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]