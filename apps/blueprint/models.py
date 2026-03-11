import uuid
from django.db import models
from apps.common.models import TimeStampedModel


class School(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    branch_code = models.CharField(max_length=10, blank=True)
    address = models.TextField(blank=True)
    contact_number = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    logo = models.CharField(max_length=255, blank=True)
    subscription_status = models.CharField(max_length=20, default="active")
    subscription_start_date = models.DateField(null=True, blank=True)
    subscription_end_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "blueprint_schools"


class Program(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE, related_name="programs")
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_months = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "blueprint_programs"


class Department(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=100)
    head = models.ForeignKey("blueprint.Staff", null=True, blank=True, on_delete=models.SET_NULL, related_name="head_of_department")
    description = models.TextField(blank=True)

    class Meta:
        db_table = "blueprint_departments"


class Staff(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE, related_name="staff")
    department = models.ForeignKey("blueprint.Department", null=True, blank=True, on_delete=models.SET_NULL)
    staff_number = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    position = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)
    username = models.CharField(max_length=80, blank=True)

    class Meta:
        db_table = "blueprint_staff"


class StaffRole(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey("blueprint.Staff", on_delete=models.CASCADE, related_name="roles")
    role_name = models.CharField(max_length=80)
    permissions = models.JSONField(default=dict, blank=True)
    assigned_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "blueprint_staff_roles"


class Student(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE, related_name="students")
    student_number = models.CharField(max_length=32, unique=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    program = models.ForeignKey("blueprint.Program", null=True, blank=True, on_delete=models.SET_NULL)
    intake_batch = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=30, default="active")
    request_credits = models.IntegerField(default=5)

    class Meta:
        db_table = "blueprint_students"


class Course(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE, related_name="courses")
    program = models.ForeignKey("blueprint.Program", null=True, blank=True, on_delete=models.SET_NULL)
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    credit_hours = models.IntegerField(default=0)

    class Meta:
        db_table = "blueprint_courses"


class Classroom(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE, related_name="classrooms")
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    capacity = models.IntegerField(default=0)

    class Meta:
        db_table = "blueprint_classrooms"


class AcademicSession(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE, related_name="sessions")
    name = models.CharField(max_length=80)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        db_table = "blueprint_academic_sessions"


class AcademicCalendar(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE, related_name="calendars")
    year = models.IntegerField()
    term = models.CharField(max_length=50, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey("blueprint.Staff", null=True, blank=True, on_delete=models.SET_NULL)
    is_published = models.BooleanField(default=False)

    class Meta:
        db_table = "blueprint_academic_calendars"


class Module(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE)
    calendar = models.ForeignKey("blueprint.AcademicCalendar", null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "blueprint_modules"


class CourseSchedule(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE)
    course = models.ForeignKey("blueprint.Course", on_delete=models.CASCADE)
    instructor = models.ForeignKey("blueprint.Staff", null=True, blank=True, on_delete=models.SET_NULL)
    classroom = models.ForeignKey("blueprint.Classroom", null=True, blank=True, on_delete=models.SET_NULL)
    session = models.ForeignKey("blueprint.AcademicSession", null=True, blank=True, on_delete=models.SET_NULL)
    module = models.ForeignKey("blueprint.Module", null=True, blank=True, on_delete=models.SET_NULL)
    class_name = models.CharField(max_length=120, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "blueprint_course_schedules"


class StudentEnrollment(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE)
    student = models.ForeignKey("blueprint.Student", on_delete=models.CASCADE)
    course_schedule = models.ForeignKey("blueprint.CourseSchedule", on_delete=models.CASCADE)
    enrollment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, default="enrolled")

    class Meta:
        db_table = "blueprint_student_enrollments"


class AssessmentComponent(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE)
    course_schedule = models.ForeignKey("blueprint.CourseSchedule", on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    component_type = models.CharField(max_length=50)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    max_score = models.DecimalField(max_digits=8, decimal_places=2, default=100)

    class Meta:
        db_table = "blueprint_assessment_components"


class StudentAssessment(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE)
    student = models.ForeignKey("blueprint.Student", on_delete=models.CASCADE)
    component = models.ForeignKey("blueprint.AssessmentComponent", on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=8, decimal_places=2)
    graded_by = models.ForeignKey("blueprint.Staff", null=True, blank=True, on_delete=models.SET_NULL)
    is_special_exam = models.BooleanField(default=False)

    class Meta:
        db_table = "blueprint_student_assessments"


class AttendanceRecord(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE)
    student = models.ForeignKey("blueprint.Student", on_delete=models.CASCADE)
    course_schedule = models.ForeignKey("blueprint.CourseSchedule", on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20)
    points = models.IntegerField(default=0)

    class Meta:
        db_table = "blueprint_attendance_records"


class SPR(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE)
    student = models.ForeignKey("blueprint.Student", on_delete=models.CASCADE)
    course_schedule = models.ForeignKey("blueprint.CourseSchedule", on_delete=models.CASCADE)
    final_grade = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    remarks = models.CharField(max_length=20, blank=True)
    pass_cutoff = models.DecimalField(max_digits=5, decimal_places=2, default=75)
    instructor = models.ForeignKey("blueprint.Staff", related_name="spr_submitted", null=True, blank=True, on_delete=models.SET_NULL)
    training_manager_status = models.CharField(max_length=30, default="pending")
    registrar_status = models.CharField(max_length=30, default="pending")
    is_published = models.BooleanField(default=False)
    version = models.IntegerField(default=1)

    class Meta:
        db_table = "blueprint_spr"


class SPRVersion(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spr = models.ForeignKey("blueprint.SPR", on_delete=models.CASCADE, related_name="versions")
    version_number = models.IntegerField()
    data_json = models.JSONField(default=dict, blank=True)
    changed_by = models.ForeignKey("blueprint.Staff", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "blueprint_spr_versions"


class ExamSchedule(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE)
    course_schedule = models.ForeignKey("blueprint.CourseSchedule", null=True, blank=True, on_delete=models.SET_NULL)
    exam_type = models.CharField(max_length=30)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    classroom = models.ForeignKey("blueprint.Classroom", null=True, blank=True, on_delete=models.SET_NULL)
    invigilator = models.ForeignKey("blueprint.Staff", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "blueprint_exam_schedules"


class ExamPermit(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE)
    student = models.ForeignKey("blueprint.Student", on_delete=models.CASCADE)
    exam_schedule = models.ForeignKey("blueprint.ExamSchedule", on_delete=models.CASCADE)
    fee_verified = models.BooleanField(default=False)
    training_manager_approved = models.BooleanField(default=False)
    barcode = models.CharField(max_length=120, blank=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = "blueprint_exam_permits"


class FeeStructure(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE)
    program = models.ForeignKey("blueprint.Program", null=True, blank=True, on_delete=models.SET_NULL)
    academic_year = models.IntegerField(null=True, blank=True)
    tuition = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = "blueprint_fee_structures"


class StudentFee(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE)
    student = models.ForeignKey("blueprint.Student", on_delete=models.CASCADE)
    fee_structure = models.ForeignKey("blueprint.FeeStructure", null=True, blank=True, on_delete=models.SET_NULL)
    payment_plan = models.CharField(max_length=20, default="monthly")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, default="unpaid")

    class Meta:
        db_table = "blueprint_student_fees"


class PaymentTransaction(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE)
    student_fee = models.ForeignKey("blueprint.StudentFee", null=True, blank=True, on_delete=models.SET_NULL)
    receipt_number = models.CharField(max_length=80, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    method = models.CharField(max_length=30, blank=True)

    class Meta:
        db_table = "blueprint_payment_transactions"


class MonthlyInstallment(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE)
    student_fee = models.ForeignKey("blueprint.StudentFee", on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid = models.BooleanField(default=False)

    class Meta:
        db_table = "blueprint_monthly_installments"


class StudentRequest(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE)
    student = models.ForeignKey("blueprint.Student", on_delete=models.CASCADE)
    request_type = models.CharField(max_length=80)
    details = models.TextField(blank=True)
    credits_used = models.IntegerField(default=1)
    status = models.CharField(max_length=30, default="pending")

    class Meta:
        db_table = "blueprint_student_requests"


class Enquiry(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    source = models.CharField(max_length=50, blank=True)
    details = models.TextField(blank=True)

    class Meta:
        db_table = "blueprint_enquiries"


class WebsiteContent(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE)
    content_type = models.CharField(max_length=30)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    content = models.TextField(blank=True)
    published = models.BooleanField(default=False)

    class Meta:
        db_table = "blueprint_website_content"


class ActivityLog(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("blueprint.School", on_delete=models.CASCADE, null=True, blank=True)
    user_type = models.CharField(max_length=20)
    user_id = models.CharField(max_length=100)
    action = models.CharField(max_length=120)
    entity_type = models.CharField(max_length=80, blank=True)
    entity_id = models.CharField(max_length=100, blank=True)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    ip_address = models.CharField(max_length=45, blank=True)

    class Meta:
        db_table = "blueprint_activity_logs"
