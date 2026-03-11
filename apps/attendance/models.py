from django.db import models
from apps.common.models import TenantScopedModel, TimeStampedModel

class AttendancePolicy(TenantScopedModel):
    program = models.ForeignKey("academics.Program", on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey("academics.Course", on_delete=models.SET_NULL, null=True, blank=True)
    minimum_attendance_percent = models.DecimalField(max_digits=5, decimal_places=2)
    warning_threshold_percent = models.DecimalField(max_digits=5, decimal_places=2)
    bar_exam_threshold_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = "attendance_policies"

class AttendanceSession(TenantScopedModel):
    course_schedule = models.ForeignKey("academics.CourseSchedule", on_delete=models.CASCADE, related_name="attendance_sessions")
    course = models.ForeignKey("academics.Course", on_delete=models.PROTECT)
    class_obj = models.ForeignKey("academics.Class", on_delete=models.PROTECT, db_column="class_id")
    taken_by_staff_profile = models.ForeignKey("hr.StaffProfile", on_delete=models.PROTECT)
    session_date = models.DateField()
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, default="open")
    class Meta:
        db_table = "attendance_sessions"
        unique_together = [("course_schedule", "session_date", "starts_at")]

class StudentAttendanceRecord(TimeStampedModel):
    attendance_session = models.ForeignKey("attendance.AttendanceSession", on_delete=models.CASCADE, related_name="records")
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="attendance_records")
    attendance_status = models.CharField(max_length=20)
    marked_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    class Meta:
        db_table = "student_attendance_records"
        unique_together = [("attendance_session", "student_profile")]

class AttendanceAdjustment(TimeStampedModel):
    student_attendance_record = models.ForeignKey("attendance.StudentAttendanceRecord", on_delete=models.CASCADE, related_name="adjustments")
    requested_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="attendance_adjustment_requests")
    approved_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="attendance_adjustment_approvals")
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    reason = models.TextField()
    approval_status = models.CharField(max_length=20, default="pending")
    approved_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "attendance_adjustments"

class AttendanceSummary(TimeStampedModel):
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="attendance_summaries")
    course = models.ForeignKey("academics.Course", on_delete=models.CASCADE)
    term = models.ForeignKey("academics.Term", on_delete=models.CASCADE)
    sessions_total = models.PositiveIntegerField(default=0)
    present_total = models.PositiveIntegerField(default=0)
    absent_total = models.PositiveIntegerField(default=0)
    late_total = models.PositiveIntegerField(default=0)
    attendance_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_computed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "attendance_summaries"
        unique_together = [("student_profile", "course", "term")]

class AttendanceWarning(TimeStampedModel):
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="attendance_warnings")
    course = models.ForeignKey("academics.Course", on_delete=models.CASCADE)
    term = models.ForeignKey("academics.Term", on_delete=models.CASCADE)
    generated_from_summary = models.ForeignKey("attendance.AttendanceSummary", on_delete=models.SET_NULL, null=True, blank=True)
    warning_type = models.CharField(max_length=50)
    threshold_percent = models.DecimalField(max_digits=5, decimal_places=2)
    actual_percent = models.DecimalField(max_digits=5, decimal_places=2)
    issued_on = models.DateField()
    status = models.CharField(max_length=50, default="active")
    class Meta:
        db_table = "attendance_warnings"
