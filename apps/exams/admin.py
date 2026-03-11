from django.contrib import admin
from .models import Exam, ExamSchedule, StudentExamResult
from django.http import HttpResponse
import csv
from apps.common.models import AuditLog


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'course', 'is_published']
    actions = ['export_results']

    def export_results(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="exam_results.csv"'
        writer = csv.writer(response)
        writer.writerow(['exam_id', 'exam_title', 'student_number', 'score', 'grade'])
        total = 0
        for e in queryset:
            for r in e.results.select_related('student_profile'):
                writer.writerow([e.pk, e.title, getattr(r.student_profile, 'student_number', ''), r.score, r.grade])
                total += 1
        try:
            AuditLog.objects.create(
                tenant=getattr(request.user, 'tenant', None),
                user=request.user,
                table_name='student_exam_results',
                record_pk=str(total),
                operation='export_exam_results',
                new_values_json={'exported': total},
            )
        except Exception:
            pass
        return response

    export_results.short_description = 'Export exam results (CSV)'


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ['exam', 'scheduled_at', 'venue', 'duration_minutes']


@admin.register(StudentExamResult)
class StudentExamResultAdmin(admin.ModelAdmin):
    list_display = ['exam', 'student_profile', 'score', 'grade']
from django.contrib import admin
from .models import (
    ExamType, ExamSession, ExamPaper, ExamSeating, ExamAttendance, ExamResult, ExamResultAdjustment
)

@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "tenant")
    search_fields = ("name", "code")
    list_filter = ("is_active",)

@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ("name", "exam_type", "term", "start_date", "end_date", "is_active", "tenant")
    search_fields = ("name",)
    list_filter = ("exam_type", "term", "is_active")

@admin.register(ExamPaper)
class ExamPaperAdmin(admin.ModelAdmin):
    list_display = ("exam_session", "course", "class_obj", "max_score", "created_by", "created_at")
    search_fields = ("exam_session__name", "course__code")
    list_filter = ("exam_session", "course")

@admin.register(ExamSeating)
class ExamSeatingAdmin(admin.ModelAdmin):
    list_display = ("exam_session", "class_obj", "classroom", "seat_number", "student_profile")
    search_fields = ("seat_number", "student_profile__student_id")
    list_filter = ("exam_session", "class_obj", "classroom")

@admin.register(ExamAttendance)
class ExamAttendanceAdmin(admin.ModelAdmin):
    list_display = ("exam_session", "student_profile", "attended", "attendance_time")
    search_fields = ("student_profile__student_id",)
    list_filter = ("exam_session", "attended")

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ("exam_session", "student_profile", "course", "raw_score", "adjusted_score", "graded_by", "published_at")
    search_fields = ("student_profile__student_id", "course__code")
    list_filter = ("exam_session", "course")

@admin.register(ExamResultAdjustment)
class ExamResultAdjustmentAdmin(admin.ModelAdmin):
    list_display = ("exam_result", "requested_by", "approved_by", "old_score", "new_score", "approval_status", "approved_at")
    search_fields = ("reason",)
    list_filter = ("approval_status",)
