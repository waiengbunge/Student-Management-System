from rest_framework import serializers
from .models import (
    RequestType, Request, RequestComment, RequestAttachment
)

class RequestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestType
        fields = "__all__"

class RequestCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestComment
        fields = "__all__"

class RequestAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestAttachment
        fields = "__all__"

class RequestSerializer(serializers.ModelSerializer):
    comments = RequestCommentSerializer(many=True, read_only=True)
    attachments = RequestAttachmentSerializer(many=True, read_only=True)
    class Meta:
        model = Request
        fields = "__all__"
