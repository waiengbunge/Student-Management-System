from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import (
    Assessment, AssessmentItem, StudentAssessment, AssessmentAdjustment, AssessmentFeedback,
    GradingScheme, GradingSchemeItem, AssessmentComponent, PassFailRule, GradePublicationBatch
)
from apps.common.models import AuditLog
from django.contrib import admin
from .models import (
    GradingScheme, GradingSchemeItem, AssessmentComponent, AssessmentItem, StudentAssessment,
    AssessmentAdjustment, AssessmentFeedback, PassFailRule, GradePublicationBatch
)

@admin.register(GradingScheme)
class GradingSchemeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "pass_mark", "is_default", "tenant")
    search_fields = ("name", "code")
    list_filter = ("is_default",)

@admin.register(GradingSchemeItem)
class GradingSchemeItemAdmin(admin.ModelAdmin):
    list_display = ("grading_scheme", "grade_letter", "min_score", "max_score", "grade_point")
    search_fields = ("grade_letter",)
    list_filter = ("grading_scheme",)

@admin.register(AssessmentComponent)
class AssessmentComponentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "course", "term", "weight_percent", "is_required", "tenant")
    search_fields = ("name", "code")
    list_filter = ("course", "term", "is_required")

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'assessment_type', 'scheduled_at']
    actions = ['export_assessment_scores']

    def export_assessment_scores(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="assessment_scores.csv"'
        writer = csv.writer(response)
        writer.writerow(['assessment_id', 'assessment_name', 'student_number', 'score', 'grade'])
        total = 0
        for a in queryset:
            for s in a.student_scores.select_related('student_profile__user'):
                sn = getattr(s.student_profile, 'student_number', '')
                writer.writerow([a.pk, a.name, sn, s.score, s.grade])
                total += 1
        try:
            AuditLog.objects.create(
                tenant=getattr(request.user, 'tenant', None),
                user=request.user,
                table_name='student_assessments',
                record_pk=str(total),
                operation='export_assessment_scores',
                new_values_json={'exported': total},
            )
        except Exception:
            pass
        return response

    export_assessment_scores.short_description = 'Export assessment scores (CSV)'

@admin.register(AssessmentAdjustment)
class AssessmentAdjustmentAdmin(admin.ModelAdmin):
    list_display = ("student_assessment", "requested_by", "approved_by", "old_score", "new_score", "approval_status", "approved_at")
    search_fields = ("reason",)
    list_filter = ("approval_status",)

@admin.register(AssessmentFeedback)
class AssessmentFeedbackAdmin(admin.ModelAdmin):
    list_display = ("student_assessment", "staff_profile", "visibility")
    search_fields = ("feedback_text",)
    list_filter = ("visibility",)

@admin.register(PassFailRule)
class PassFailRuleAdmin(admin.ModelAdmin):
    list_display = ("rule_name", "program", "course", "minimum_total_score", "is_active", "tenant")
    search_fields = ("rule_name",)
    list_filter = ("is_active", "program", "course")

@admin.register(GradePublicationBatch)
class GradePublicationBatchAdmin(admin.ModelAdmin):
    list_display = ("batch_name", "term", "course", "published_by", "published_at", "status", "tenant")
    search_fields = ("batch_name",)
    list_filter = ("status", "term", "course")
