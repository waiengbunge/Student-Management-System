from django.contrib import admin
from django.http import HttpResponse
import csv

from .models import Program, Course, Class, ClassLevel, Classroom
from apps.students.models import Enrollment
from apps.common.models import AuditLog


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'tenant', 'campus', 'status']
    search_fields = ['name', 'code']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'tenant', 'status']
    search_fields = ['name', 'code']


@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant']


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'campus', 'capacity']


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'program', 'campus', 'capacity', 'current_enrollment', 'is_full']
    search_fields = ['name', 'code']
    actions = ['export_roster_csv']

    def current_enrollment(self, obj):
        return Enrollment.objects.filter(class_obj=obj, status='active').count()
    current_enrollment.short_description = 'Current Enrollment'

    def is_full(self, obj):
        cap = getattr(obj, 'capacity', None)
        if cap is None:
            return False
        return self.current_enrollment(obj) >= cap
    is_full.boolean = True
    is_full.short_description = 'Full'

    def export_roster_csv(self, request, queryset):
        # Export roster for selected classes
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="class_roster.csv"'
        writer = csv.writer(response)
        writer.writerow(['class_code', 'class_name', 'student_number', 'student_email', 'student_name'])
        for cls in queryset:
            enrolls = Enrollment.objects.filter(class_obj=cls, status='active').select_related('student_profile__user')
            for e in enrolls:
                student = e.student_profile
                email = student.user.email if student.user else ''
                name = f"{getattr(student, 'student_number', '')}"
                writer.writerow([cls.code, cls.name, getattr(student, 'student_number', ''), email, name])
        try:
            # record audit entry summarizing export
            AuditLog.objects.create(
                tenant=getattr(request.user, 'tenant', None),
                user=request.user,
                table_name='classes',
                record_pk=','.join(str(c.pk) for c in queryset),
                operation='export_roster',
                old_values_json=None,
                new_values_json={'export_count': sum(Enrollment.objects.filter(class_obj=c, status='active').count() for c in queryset)},
                changed_at=None,
            )
        except Exception:
            pass
        return response
    export_roster_csv.short_description = 'Export roster as CSV'
