from django.db import models
from apps.common.models import TenantScopedModel, TimeStampedModel


class Assessment(TenantScopedModel):
    program = models.ForeignKey("academics.Program", on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey("academics.Course", on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    assessment_type = models.CharField(max_length=50, default='exam')
    scheduled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'assessments'


class AssessmentItem(TimeStampedModel):
    assessment = models.ForeignKey('assessments.Assessment', on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=255)
    max_score = models.DecimalField(max_digits=8, decimal_places=2, default=100)

    class Meta:
        db_table = 'assessment_items'


class StudentAssessment(TimeStampedModel):
    assessment = models.ForeignKey('assessments.Assessment', on_delete=models.CASCADE, related_name='student_scores')
    student_profile = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='assessments')
    score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=10, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'student_assessments'
        unique_together = [('assessment', 'student_profile')]
from django.db import models
from apps.common.models import TenantScopedModel, TimeStampedModel

class GradingScheme(TenantScopedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50)
    pass_mark = models.DecimalField(max_digits=5, decimal_places=2)
    is_default = models.BooleanField(default=False)
    class Meta:
        db_table = "grading_schemes"
        unique_together = [("tenant", "code")]

class GradingSchemeItem(TimeStampedModel):
    grading_scheme = models.ForeignKey("assessments.GradingScheme", on_delete=models.CASCADE, related_name="items")
    grade_letter = models.CharField(max_length=10)
    min_score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    remark = models.CharField(max_length=120, blank=True)
    class Meta:
        db_table = "grading_scheme_items"
        unique_together = [("grading_scheme", "grade_letter")]

class AssessmentComponent(TenantScopedModel):
    course = models.ForeignKey("academics.Course", on_delete=models.CASCADE, related_name="assessment_components")
    term = models.ForeignKey("academics.Term", on_delete=models.SET_NULL, null=True, blank=True)
    grading_scheme = models.ForeignKey("assessments.GradingScheme", on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50)
    weight_percent = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=8, decimal_places=2)
    component_order = models.PositiveIntegerField(default=1)
    is_required = models.BooleanField(default=True)
    class Meta:
        db_table = "assessment_components"
        unique_together = [("tenant", "course", "term", "code")]

class AssessmentItem(TimeStampedModel):
    assessment_component = models.ForeignKey("assessments.AssessmentComponent", on_delete=models.CASCADE, related_name="items")
    class_obj = models.ForeignKey("academics.Class", on_delete=models.SET_NULL, null=True, blank=True, db_column="class_id")
    course_schedule = models.ForeignKey("academics.CourseSchedule", on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    assessment_date = models.DateField(null=True, blank=True)
    max_score = models.DecimalField(max_digits=8, decimal_places=2)
    contributes_to_final = models.BooleanField(default=True)
    class Meta:
        db_table = "assessment_items"

class StudentAssessment(TimeStampedModel):
    assessment_item = models.ForeignKey("assessments.AssessmentItem", on_delete=models.CASCADE, related_name="student_assessments")
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="student_assessments")
    marked_by_staff_profile = models.ForeignKey("hr.StaffProfile", on_delete=models.SET_NULL, null=True, blank=True)
    raw_score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    adjusted_score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_absent = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "student_assessments"
        unique_together = [("assessment_item", "student_profile")]

class AssessmentAdjustment(TimeStampedModel):
    student_assessment = models.ForeignKey("assessments.StudentAssessment", on_delete=models.CASCADE, related_name="adjustments")
    requested_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="assessment_adjustment_requests")
    approved_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="assessment_adjustment_approvals")
    old_score = models.DecimalField(max_digits=8, decimal_places=2)
    new_score = models.DecimalField(max_digits=8, decimal_places=2)
    reason = models.TextField()
    approval_status = models.CharField(max_length=20, default="pending")
    approved_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "assessment_adjustments"

class AssessmentFeedback(TimeStampedModel):
    student_assessment = models.ForeignKey("assessments.StudentAssessment", on_delete=models.CASCADE, related_name="feedback_entries")
    staff_profile = models.ForeignKey("hr.StaffProfile", on_delete=models.CASCADE)
    feedback_text = models.TextField()
    visibility = models.CharField(max_length=20, default="internal")
    class Meta:
        db_table = "assessment_feedback"

class PassFailRule(TenantScopedModel):
    program = models.ForeignKey("academics.Program", on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey("academics.Course", on_delete=models.SET_NULL, null=True, blank=True)
    rule_name = models.CharField(max_length=120)
    minimum_total_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    minimum_exam_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    minimum_attendance_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    requires_all_components_passed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = "pass_fail_rules"

class GradePublicationBatch(TenantScopedModel):
    term = models.ForeignKey("academics.Term", on_delete=models.CASCADE)
    course = models.ForeignKey("academics.Course", on_delete=models.SET_NULL, null=True, blank=True)
    published_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    batch_name = models.CharField(max_length=120)
    published_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, default="draft")
    class Meta:
        db_table = "grade_publication_batches"
