from django.db import models
from apps.common.models import CampusScopedModel, TenantScopedModel, TimeStampedModel

class GuardianProfile(TenantScopedModel):
    user = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="guardian_profiles")
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    relationship_type = models.CharField(max_length=50, blank=True)
    occupation = models.CharField(max_length=120, blank=True)
    class Meta:
        db_table = "guardian_profiles"

class StudentProfile(CampusScopedModel):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="student_profile")
    current_program = models.ForeignKey("academics.Program", on_delete=models.SET_NULL, null=True, blank=True, related_name="current_students")
    admission_offer = models.ForeignKey("admissions.AdmissionOffer", on_delete=models.SET_NULL, null=True, blank=True)
    student_number = models.CharField(max_length=50)
    admitted_on = models.DateField(null=True, blank=True)
    current_status = models.CharField(max_length=50, default="active")
    class Meta:
        db_table = "student_profiles"
        unique_together = [("tenant", "student_number")]

class StudentGuardian(TimeStampedModel):
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="student_guardians")
    guardian_profile = models.ForeignKey("students.GuardianProfile", on_delete=models.CASCADE, related_name="guardian_students")
    relationship_type = models.CharField(max_length=50)
    is_primary = models.BooleanField(default=False)
    is_emergency_contact = models.BooleanField(default=False)
    class Meta:
        db_table = "student_guardians"
        unique_together = [("student_profile", "guardian_profile")]

class StudentAddress(TimeStampedModel):
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="addresses")
    address_type = models.CharField(max_length=30)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    province = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, default="Papua New Guinea")
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    class Meta:
        db_table = "student_addresses"

class StudentDocument(TimeStampedModel):
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="documents")
    file_upload = models.ForeignKey("common.FileUpload", on_delete=models.CASCADE, related_name="student_documents")
    document_type = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "student_documents"

class StudentStatusHistory(TimeStampedModel):
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="status_history")
    changed_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    old_status = models.CharField(max_length=50, blank=True)
    new_status = models.CharField(max_length=50)
    reason = models.TextField(blank=True)
    changed_at = models.DateTimeField()
    class Meta:
        db_table = "student_status_history"

class StudentProgramHistory(TimeStampedModel):
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="program_history")
    program = models.ForeignKey("academics.Program", on_delete=models.PROTECT)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    reason = models.TextField(blank=True)
    class Meta:
        db_table = "student_program_history"

class Enrollment(TenantScopedModel):
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="enrollments")
    program = models.ForeignKey("academics.Program", on_delete=models.PROTECT, related_name="enrollments")
    academic_year = models.ForeignKey("academics.AcademicYear", on_delete=models.PROTECT)
    term = models.ForeignKey("academics.Term", on_delete=models.PROTECT)
    class_obj = models.ForeignKey("academics.Class", on_delete=models.SET_NULL, null=True, blank=True, db_column="class_id")
    payment_plan = models.ForeignKey("finance.PaymentPlan", on_delete=models.SET_NULL, null=True, blank=True)
    enrollment_number = models.CharField(max_length=50)
    enrolled_on = models.DateField()
    status = models.CharField(max_length=50)
    class Meta:
        db_table = "enrollments"
        unique_together = [
            ("tenant", "enrollment_number"),
            ("student_profile", "program", "academic_year", "term"),
        ]

class EnrollmentStatusHistory(TimeStampedModel):
    enrollment = models.ForeignKey("students.Enrollment", on_delete=models.CASCADE, related_name="status_history")
    changed_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    old_status = models.CharField(max_length=50, blank=True)
    new_status = models.CharField(max_length=50)
    changed_at = models.DateTimeField()
    remarks = models.TextField(blank=True)
    class Meta:
        db_table = "enrollment_status_history"

class ReEnrollment(TimeStampedModel):
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="reenrollments")
    previous_enrollment = models.ForeignKey("students.Enrollment", on_delete=models.PROTECT, related_name="previous_reenrollment_set")
    new_enrollment = models.ForeignKey("students.Enrollment", on_delete=models.PROTECT, related_name="new_reenrollment_set")
    processed_on = models.DateField()
    remarks = models.TextField(blank=True)
    class Meta:
        db_table = "reenrollments"

class Withdrawal(TimeStampedModel):
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="withdrawals")
    enrollment = models.ForeignKey("students.Enrollment", on_delete=models.PROTECT, related_name="withdrawals")
    requested_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    withdrawal_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=50)
    class Meta:
        db_table = "withdrawals"

class WithdrawalClearance(TimeStampedModel):
    withdrawal = models.ForeignKey("students.Withdrawal", on_delete=models.CASCADE, related_name="clearances")
    department = models.ForeignKey("hr.Department", on_delete=models.PROTECT)
    cleared_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    clearance_status = models.CharField(max_length=50)
    remarks = models.TextField(blank=True)
    cleared_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "withdrawal_clearances"
        unique_together = [("withdrawal", "department")]
