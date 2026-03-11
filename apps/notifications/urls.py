from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NotificationTypeViewSet, NotificationViewSet, NotificationLogViewSet

router = DefaultRouter()
router.register(r"types", NotificationTypeViewSet)
router.register(r"notifications", NotificationViewSet)
router.register(r"logs", NotificationLogViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
