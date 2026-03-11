from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    RequestTypeViewSet,
    RequestViewSet,
    RequestCommentViewSet,
    RequestAttachmentViewSet,
)

router = DefaultRouter()
router.register(r"types", RequestTypeViewSet)
router.register(r"requests", RequestViewSet)
router.register(r"comments", RequestCommentViewSet)
router.register(r"attachments", RequestAttachmentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
