from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import (
	AttendancePolicy,
	AttendanceSession,
	StudentAttendanceRecord,
	AttendanceAdjustment,
	AttendanceSummary,
	AttendanceWarning,
)
from apps.common.models import AuditLog


@admin.register(AttendancePolicy)
class AttendancePolicyAdmin(admin.ModelAdmin):
	list_display = ['id', 'program', 'course', 'minimum_attendance_percent', 'is_active']


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
	list_display = ['id', 'course', 'class_obj', 'session_date', 'starts_at', 'taken_by_staff_profile', 'status']
	actions = ['export_session_records_csv', 'compute_summaries']

	def export_session_records_csv(self, request, queryset):
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="attendance_records.csv"'
		writer = csv.writer(response)
		writer.writerow(['session_id', 'course', 'class', 'session_date', 'student_number', 'student_name', 'attendance_status', 'marked_at', 'remarks'])
		total = 0
		for sess in queryset:
			for r in StudentAttendanceRecord.objects.filter(attendance_session=sess).select_related('student_profile__user'):
				student = r.student_profile
				name = ''
				try:
					name = f"{student.user.profile.first_name} {student.user.profile.last_name}"
				except Exception:
					name = ''
				writer.writerow([sess.pk, getattr(sess.course, 'name', ''), getattr(sess.class_obj, 'name', ''), sess.session_date, getattr(student, 'student_number', ''), name, r.attendance_status, r.marked_at, r.remarks])
				total += 1
		try:
			AuditLog.objects.create(
				tenant=getattr(request.user, 'tenant', None),
				user=request.user,
				table_name='student_attendance_records',
				record_pk=str(total),
				operation='export_attendance',
				old_values_json=None,
				new_values_json={'exported_records': total},
			)
		except Exception:
			pass
		return response

	export_session_records_csv.short_description = 'Export attendance records for selected sessions (CSV)'

	def compute_summaries(self, request, queryset):
		# compute/update AttendanceSummary rows for sessions' courses/terms
		updated = 0
		for sess in queryset:
			records = StudentAttendanceRecord.objects.filter(attendance_session=sess).select_related('student_profile')
			for r in records:
				try:
					# find or create summary for student/course/term (term may be on course_schedule)
					term = getattr(sess.course_schedule, 'term', None)
					summary, created = AttendanceSummary.objects.get_or_create(student_profile=r.student_profile, course=sess.course, term=term)
					summary.sessions_total = summary.sessions_total + 1
					if r.attendance_status.lower() in ('present', 'p'):
						summary.present_total = summary.present_total + 1
					elif r.attendance_status.lower() in ('absent', 'a'):
						summary.absent_total = summary.absent_total + 1
					elif r.attendance_status.lower() in ('late', 'l'):
						summary.late_total = summary.late_total + 1
					# recompute percent
					if summary.sessions_total > 0:
						summary.attendance_percent = (summary.present_total / summary.sessions_total) * 100
					summary.save()
					updated += 1
				except Exception:
					continue
		try:
			AuditLog.objects.create(
				tenant=getattr(request.user, 'tenant', None),
				user=request.user,
				table_name='attendance_summaries',
				record_pk=str(updated),
				operation='compute_summaries',
				old_values_json=None,
				new_values_json={'updated_rows': updated},
			)
		except Exception:
			pass
		self.message_user(request, f'Computed/updated {updated} summary items')

	compute_summaries.short_description = 'Compute attendance summaries for selected sessions'


@admin.register(StudentAttendanceRecord)
class StudentAttendanceRecordAdmin(admin.ModelAdmin):
	list_display = ['attendance_session', 'student_profile', 'attendance_status', 'marked_at']


@admin.register(AttendanceAdjustment)
class AttendanceAdjustmentAdmin(admin.ModelAdmin):
	list_display = ['student_attendance_record', 'requested_by', 'approved_by', 'approval_status']


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
	list_display = ['student_profile', 'course', 'term', 'attendance_percent', 'sessions_total']


@admin.register(AttendanceWarning)
class AttendanceWarningAdmin(admin.ModelAdmin):
	list_display = ['student_profile', 'course', 'term', 'warning_type', 'actual_percent', 'status']
