from django.utils import timezone

from .models import ExamSession, StudentExamResult


class ExamService:
    """Service methods for exam workflows."""
    @staticmethod
    def schedule_exam(exam_session_id, course_id, class_id=None):
        try:
            es = ExamSession.objects.get(pk=exam_session_id)
        except ExamSession.DoesNotExist:
            return None
        es.course_id = course_id
        if class_id:
            es.class_id = class_id
        es.save()
        return es

    @staticmethod
    def record_exam_attendance(exam_session_id, student_profile_id, attended):
        # create or update StudentExamResult attendance flag
        obj, _ = StudentExamResult.objects.get_or_create(exam_session_id=exam_session_id, student_profile_id=student_profile_id)
        obj.attended = bool(attended)
        obj.save(update_fields=['attended'])
        return obj

    @staticmethod
    def publish_exam_results(exam_session_id):
        now = timezone.now()
        results = StudentExamResult.objects.filter(exam_session_id=exam_session_id, published_at__isnull=True)
        count = 0
        for r in results:
            r.published_at = now
            r.save(update_fields=['published_at'])
            count += 1
        return count

    @staticmethod
    def apply_result_adjustment(adjustment_id):
        # simple placeholder: find result by id and mark adjusted
        try:
            r = StudentExamResult.objects.get(pk=adjustment_id)
        except StudentExamResult.DoesNotExist:
            return False
        # flip an 'adjusted' flag if present, else set published_at
        if hasattr(r, 'adjusted_score'):
            # no-op for now
            pass
        r.published_at = r.published_at or timezone.now()
        r.save(update_fields=['published_at'])
        return True
