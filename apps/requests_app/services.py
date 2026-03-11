from django.utils import timezone
from .models import Request, RequestComment, RequestAttachment
from django.core.files.base import ContentFile


class RequestService:
    """Service methods for request workflows."""
    @staticmethod
    def create_request(request_type_id, requested_by_id, subject, description, student_profile_id=None, staff_profile_id=None):
        r = Request.objects.create(
            request_type_id=request_type_id,
            requested_by_id=requested_by_id,
            student_profile_id=student_profile_id,
            staff_profile_id=staff_profile_id,
            subject=subject,
            description=description,
            status='pending'
        )
        return r

    @staticmethod
    def add_comment(request_id, commented_by_id, comment):
        rc = RequestComment.objects.create(
            request_id=request_id,
            commented_by_id=commented_by_id,
            comment=comment
        )
        return rc

    @staticmethod
    def add_attachment(request_id, uploaded_by_id, file):
        # `file` may be a file-like object or bytes; support both
        if hasattr(file, 'read'):
            content = file.read()
            name = getattr(file, 'name', 'attachment')
        else:
            content = file
            name = 'attachment'

        fa = RequestAttachment.objects.create(
            request_id=request_id,
            uploaded_by_id=uploaded_by_id,
        )
        fa.file.save(name, ContentFile(content))
        fa.save()
        return fa

    @staticmethod
    def close_request(request_id, closed_by_id=None):
        try:
            r = Request.objects.get(pk=request_id)
        except Request.DoesNotExist:
            return False
        r.status = 'closed'
        r.closed_at = timezone.now()
        r.save(update_fields=['status', 'closed_at'])
        return True
