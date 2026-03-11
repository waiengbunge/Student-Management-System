from rest_framework import viewsets
from apps.accounts.drf_permissions import RolePermissionDRF

from .models import RequestType, Request, RequestComment, RequestAttachment
from .serializers import (
    RequestTypeSerializer,
    RequestSerializer,
    RequestCommentSerializer,
    RequestAttachmentSerializer,
)


class RequestTypeViewSet(viewsets.ModelViewSet):
    queryset = RequestType.objects.all()
    serializer_class = RequestTypeSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'requests.manage'


class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'requests.manage'


class RequestCommentViewSet(viewsets.ModelViewSet):
    queryset = RequestComment.objects.all()
    serializer_class = RequestCommentSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'requests.manage'


class RequestAttachmentViewSet(viewsets.ModelViewSet):
    queryset = RequestAttachment.objects.all()
    serializer_class = RequestAttachmentSerializer
    permission_classes = [RolePermissionDRF]
    required_permission = 'requests.manage'
