from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet, PermissionViewSet, UserRoleViewSet, ApiKeyViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('roles', RoleViewSet, basename='role')
router.register('permissions', PermissionViewSet, basename='permission')
router.register('user-roles', UserRoleViewSet, basename='userrole')
router.register('api-keys', ApiKeyViewSet, basename='apikey')

urlpatterns = [
    path('', include(router.urls)),
]
