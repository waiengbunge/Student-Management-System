from django.contrib import admin
from django.http import HttpResponse
import csv

from .models import StudentProfile, Enrollment, GuardianProfile
from apps.common.models import AuditLog


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
	list_display = ['student_number', 'user', 'tenant', 'campus', 'current_status']
	search_fields = ['student_number', 'user__email']


@admin.register(GuardianProfile)
class GuardianProfileAdmin(admin.ModelAdmin):
	list_display = ['full_name', 'phone', 'email']
	search_fields = ['full_name', 'email']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
	list_display = ['enrollment_number', 'student_profile', 'program', 'academic_year', 'term', 'class_obj', 'status']
	actions = ['approve_enrollments', 'export_enrollments_csv']

	def approve_enrollments(self, request, queryset):
		updated = queryset.update(status='active')
		self.message_user(request, f"Marked {updated} enrollments as active")
		try:
			AuditLog.objects.create(
				tenant=getattr(request.user, 'tenant', None),
				user=request.user,
				table_name='enrollments',
				record_pk=','.join(str(e.pk) for e in queryset),
				operation='approve_enrollments',
				old_values_json=None,
				new_values_json={'approved_count': updated},
				changed_at=None,
			)
		except Exception:
			pass
	approve_enrollments.short_description = 'Approve selected enrollments (mark active)'

	def export_enrollments_csv(self, request, queryset):
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="enrollments.csv"'
		writer = csv.writer(response)
		writer.writerow(['enrollment_number', 'student_number', 'student_email', 'program', 'term', 'class'])
		for e in queryset.select_related('student_profile__user', 'program', 'term', 'class_obj'):
			student = e.student_profile
			email = student.user.email if student.user else ''
			writer.writerow([e.enrollment_number, getattr(student, 'student_number', ''), email, getattr(e.program, 'name', ''), getattr(e.term, 'name', ''), getattr(e.class_obj, 'name', '')])
		try:
			AuditLog.objects.create(
				tenant=getattr(request.user, 'tenant', None),
				user=request.user,
				table_name='enrollments',
				record_pk=','.join(str(e.pk) for e in queryset),
				operation='export_enrollments',
				old_values_json=None,
				new_values_json={'export_count': queryset.count()},
				changed_at=None,
			)
		except Exception:
			pass
		return response
	export_enrollments_csv.short_description = 'Export selected enrollments as CSV'

