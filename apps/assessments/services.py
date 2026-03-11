# Service layer for assessments app
# Implement business logic, calculations, and utilities here

from django.utils import timezone
from decimal import Decimal
from .models import (
    AssessmentComponent, AssessmentItem, StudentAssessment as StudentAssessmentItem,
    StudentAssessment, AssessmentAdjustment, GradePublicationBatch, GradingSchemeItem
)


class AssessmentService:
    """Service methods for assessment workflows."""
    @staticmethod
    def calculate_final_grade(student_profile, course, term=None):
        """Calculate a simple weighted final percentage and map to a grade letter.

        Uses available `StudentAssessment` records for `assessment_item` objects
        belonging to `course` (and optional `term`). Falls back to raw_score
        when adjusted_score is not present.
        Returns a dict: {"percentage": Decimal, "grade": str}
        """
        # collect student assessments for the course/term
        qs = StudentAssessmentItem.objects.filter(student_profile=student_profile, assessment_item__course_schedule__course=course)
        if term:
            qs = qs.filter(assessment_item__assessment_component__term=term)

        total_weight = Decimal(0)
        accumulated = Decimal(0)
        for sa in qs.select_related('assessment_item__assessment_component'):
            comp = sa.assessment_item.assessment_component
            weight = getattr(comp, 'weight_percent', Decimal(0)) or Decimal(0)
            max_score = getattr(sa.assessment_item, 'max_score', Decimal(100)) or Decimal(100)
            score = sa.adjusted_score if sa.adjusted_score is not None else sa.raw_score or Decimal(0)
            try:
                pct = (Decimal(score) / Decimal(max_score)) * Decimal(100)
            except Exception:
                pct = Decimal(0)
            accumulated += (pct * (Decimal(weight) / Decimal(100)))
            total_weight += Decimal(weight)

        if total_weight == 0:
            percentage = Decimal(0)
        else:
            # normalize by total weight
            percentage = (accumulated / (total_weight / Decimal(100))).quantize(Decimal('0.01'))

        # map to grading scheme item if available: pick first grading scheme on components
        grade_letter = ''
        comp = AssessmentComponent.objects.filter(course=course).first()
        if comp and comp.grading_scheme:
            items = GradingSchemeItem.objects.filter(grading_scheme=comp.grading_scheme).order_by('-min_score')
            for gi in items:
                if gi.min_score <= percentage <= gi.max_score:
                    grade_letter = gi.grade_letter
                    break

        return {"percentage": percentage, "grade": grade_letter}

    @staticmethod
    def publish_grades(batch_id):
        """Publish all unpublished student assessments in a GradePublicationBatch.

        Marks `published_at` on `StudentAssessment` records and updates the
        `GradePublicationBatch` status and `published_at` timestamp.
        Returns number of published records.
        """
        try:
            batch = GradePublicationBatch.objects.get(pk=batch_id)
        except GradePublicationBatch.DoesNotExist:
            return 0

        now = timezone.now()
        s_qs = StudentAssessment.objects.filter(assessment_item__assessment_component__course=batch.course, published_at__isnull=True)
        count = 0
        for sa in s_qs:
            sa.published_at = now
            sa.save(update_fields=['published_at'])
            count += 1

        batch.status = 'published'
        batch.published_at = now
        batch.save(update_fields=['status', 'published_at'])
        return count

    @staticmethod
    def apply_assessment_adjustment(adjustment_id):
        """Apply an approved AssessmentAdjustment to the related StudentAssessment.

        If the adjustment is approved, update `adjusted_score` on the
        `StudentAssessment` and set `approved_at`.
        Returns True when applied.
        """
        try:
            adj = AssessmentAdjustment.objects.select_related('student_assessment').get(pk=adjustment_id)
        except AssessmentAdjustment.DoesNotExist:
            return False

        if adj.approval_status.lower() != 'approved':
            return False

        sa = adj.student_assessment
        sa.adjusted_score = adj.new_score
        sa.save(update_fields=['adjusted_score'])
        adj.approved_at = adj.approved_at or timezone.now()
        adj.save(update_fields=['approved_at'])
        return True

    @staticmethod
    def get_student_assessment_summary(student_profile, course, term=None):
        """Return a lightweight summary of student assessments for a course/term."""
        qs = StudentAssessmentItem.objects.filter(student_profile=student_profile, assessment_item__assessment_component__course=course)
        if term:
            qs = qs.filter(assessment_item__assessment_component__term=term)

        items = []
        for sa in qs.select_related('assessment_item'):
            items.append({
                'assessment_item_id': sa.assessment_item_id,
                'name': sa.assessment_item.name,
                'raw_score': sa.raw_score,
                'adjusted_score': sa.adjusted_score,
                'is_absent': sa.is_absent,
                'published_at': sa.published_at,
            })

        return {
            'student_profile_id': student_profile.pk,
            'course_id': getattr(course, 'pk', None),
            'assessments': items,
        }
