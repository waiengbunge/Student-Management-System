from django.db import models
from apps.common.models import TenantScopedModel, TimeStampedModel


class Exam(TenantScopedModel):
    program = models.ForeignKey('academics.Program', on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey('academics.Course', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        db_table = 'exams'


class ExamSchedule(TenantScopedModel):
    exam = models.ForeignKey('exams.Exam', on_delete=models.CASCADE, related_name='schedules')
    scheduled_at = models.DateTimeField()
    venue = models.CharField(max_length=255, blank=True)
    duration_minutes = models.PositiveIntegerField(default=60)

    class Meta:
        db_table = 'exam_schedules'


class StudentExamResult(TimeStampedModel):
    exam = models.ForeignKey('exams.Exam', on_delete=models.CASCADE, related_name='results')
    student_profile = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='exam_results')
    score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=10, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'student_exam_results'
        unique_together = [('exam', 'student_profile')]
from django.db import models
from apps.common.models import TenantScopedModel, TimeStampedModel

class ExamType(TenantScopedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = "exam_types"
        unique_together = [("tenant", "code")]

class ExamSession(TenantScopedModel):
    exam_type = models.ForeignKey("exams.ExamType", on_delete=models.PROTECT)
    term = models.ForeignKey("academics.Term", on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = "exam_sessions"
        unique_together = [("tenant", "exam_type", "term", "name")]

class ExamPaper(TimeStampedModel):
    exam_session = models.ForeignKey("exams.ExamSession", on_delete=models.CASCADE)
    course = models.ForeignKey("academics.Course", on_delete=models.CASCADE)
    class_obj = models.ForeignKey("academics.Class", on_delete=models.SET_NULL, null=True, blank=True, db_column="class_id")
    paper_file = models.FileField(upload_to="exam_papers/", null=True, blank=True)
    max_score = models.DecimalField(max_digits=8, decimal_places=2)
    created_by = models.ForeignKey("hr.StaffProfile", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "exam_papers"

class ExamSeating(TimeStampedModel):
    exam_session = models.ForeignKey("exams.ExamSession", on_delete=models.CASCADE)
    class_obj = models.ForeignKey("academics.Class", on_delete=models.CASCADE, db_column="class_id")
    classroom = models.ForeignKey("academics.Classroom", on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=20)
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE)
    class Meta:
        db_table = "exam_seating"
        unique_together = [("exam_session", "class_obj", "seat_number")]

class ExamAttendance(TimeStampedModel):
    exam_session = models.ForeignKey("exams.ExamSession", on_delete=models.CASCADE)
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    attendance_time = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "exam_attendance"
        unique_together = [("exam_session", "student_profile")]

class ExamResult(TimeStampedModel):
    exam_session = models.ForeignKey("exams.ExamSession", on_delete=models.CASCADE)
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE)
    course = models.ForeignKey("academics.Course", on_delete=models.CASCADE)
    raw_score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    adjusted_score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    graded_by = models.ForeignKey("hr.StaffProfile", on_delete=models.SET_NULL, null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "exam_results"
        unique_together = [("exam_session", "student_profile", "course")]

class ExamResultAdjustment(TimeStampedModel):
    exam_result = models.ForeignKey("exams.ExamResult", on_delete=models.CASCADE, related_name="adjustments")
    requested_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="exam_result_adjustment_requests")
    approved_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="exam_result_adjustment_approvals")
    old_score = models.DecimalField(max_digits=8, decimal_places=2)
    new_score = models.DecimalField(max_digits=8, decimal_places=2)
    reason = models.TextField()
    approval_status = models.CharField(max_length=20, default="pending")
    approved_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "exam_result_adjustments"
