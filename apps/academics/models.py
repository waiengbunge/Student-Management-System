from django.db import models
from apps.common.models import CampusScopedModel, TenantScopedModel, TimeStampedModel

class AcademicYear(TenantScopedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    class Meta:
        db_table = "academic_years"
        unique_together = [("tenant", "code")]

class Term(TenantScopedModel):
    academic_year = models.ForeignKey("academics.AcademicYear", on_delete=models.CASCADE, related_name="terms")
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    term_order = models.PositiveIntegerField(default=1)
    class Meta:
        db_table = "terms"
        unique_together = [("academic_year", "code")]

class Program(CampusScopedModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    award_type = models.CharField(max_length=120, blank=True)
    duration_months = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=50, default="active")
    class Meta:
        db_table = "programs"
        unique_together = [("tenant", "code")]

class ProgramVersion(TimeStampedModel):
    program = models.ForeignKey("academics.Program", on_delete=models.CASCADE, related_name="versions")
    version_number = models.CharField(max_length=30)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, default="active")
    class Meta:
        db_table = "program_versions"
        unique_together = [("program", "version_number")]

class ProgramRequirement(TimeStampedModel):
    program_version = models.ForeignKey("academics.ProgramVersion", on_delete=models.CASCADE, related_name="requirements")
    requirement_type = models.CharField(max_length=50)
    description = models.TextField()
    minimum_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    class Meta:
        db_table = "program_requirements"

class Course(TenantScopedModel):
    department = models.ForeignKey("hr.Department", on_delete=models.SET_NULL, null=True, blank=True, related_name="courses")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    credit_hours = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=50, default="active")
    class Meta:
        db_table = "courses"
        unique_together = [("tenant", "code")]

class CourseVersion(TimeStampedModel):
    course = models.ForeignKey("academics.Course", on_delete=models.CASCADE, related_name="versions")
    version_number = models.CharField(max_length=30)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = "course_versions"
        unique_together = [("course", "version_number")]

class Module(TimeStampedModel):
    program_version = models.ForeignKey("academics.ProgramVersion", on_delete=models.CASCADE, related_name="modules")
    course_version = models.ForeignKey("academics.CourseVersion", on_delete=models.CASCADE, related_name="program_modules")
    module_order = models.PositiveIntegerField(default=1)
    term_number = models.PositiveIntegerField(null=True, blank=True)
    is_core = models.BooleanField(default=True)
    class Meta:
        db_table = "modules"
        unique_together = [("program_version", "course_version")]

class ClassLevel(TenantScopedModel):
    name = models.CharField(max_length=120)
    level_order = models.PositiveIntegerField(default=1)
    class Meta:
        db_table = "class_levels"
        unique_together = [("tenant", "name")]

class Class(CampusScopedModel):
    program = models.ForeignKey("academics.Program", on_delete=models.PROTECT, related_name="classes")
    academic_year = models.ForeignKey("academics.AcademicYear", on_delete=models.PROTECT, related_name="classes")
    class_level = models.ForeignKey("academics.ClassLevel", on_delete=models.SET_NULL, null=True, blank=True, related_name="classes")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    batch_name = models.CharField(max_length=120, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, default="active")
    class Meta:
        db_table = "classes"
        unique_together = [("tenant", "code")]

class ClassMembership(TimeStampedModel):
    class_obj = models.ForeignKey("academics.Class", on_delete=models.CASCADE, related_name="memberships", db_column="class_id")
    student_profile = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="class_memberships")
    enrollment = models.ForeignKey("students.Enrollment", on_delete=models.SET_NULL, null=True, blank=True)
    joined_on = models.DateField()
    left_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, default="active")
    class Meta:
        db_table = "class_memberships"
        unique_together = [("class_obj", "student_profile")]

class Classroom(CampusScopedModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(default=0)
    room_type = models.CharField(max_length=50, blank=True)
    class Meta:
        db_table = "classrooms"
        unique_together = [("tenant", "campus", "code")]

class AcademicSession(TenantScopedModel):
    name = models.CharField(max_length=120)
    start_time = models.TimeField()
    end_time = models.TimeField()
    sort_order = models.PositiveIntegerField(default=1)
    class Meta:
        db_table = "academic_sessions"
        unique_together = [("tenant", "name")]

class InstructorAssignment(TenantScopedModel):
    staff_profile = models.ForeignKey("hr.StaffProfile", on_delete=models.PROTECT, related_name="instructor_assignments")
    course = models.ForeignKey("academics.Course", on_delete=models.PROTECT, related_name="instructor_assignments")
    class_obj = models.ForeignKey("academics.Class", on_delete=models.SET_NULL, null=True, blank=True, db_column="class_id")
    term = models.ForeignKey("academics.Term", on_delete=models.PROTECT, related_name="instructor_assignments")
    assigned_on = models.DateField()
    status = models.CharField(max_length=50, default="active")
    class Meta:
        db_table = "instructor_assignments"
        unique_together = [("staff_profile", "course", "class_obj", "term")]

class CourseSchedule(CampusScopedModel):
    class_obj = models.ForeignKey("academics.Class", on_delete=models.PROTECT, related_name="course_schedules", db_column="class_id")
    course = models.ForeignKey("academics.Course", on_delete=models.PROTECT, related_name="course_schedules")
    classroom = models.ForeignKey("academics.Classroom", on_delete=models.PROTECT, related_name="course_schedules")
    academic_session = models.ForeignKey("academics.AcademicSession", on_delete=models.PROTECT, related_name="course_schedules")
    term = models.ForeignKey("academics.Term", on_delete=models.PROTECT, related_name="course_schedules")
    instructor_assignment = models.ForeignKey("academics.InstructorAssignment", on_delete=models.SET_NULL, null=True, blank=True, related_name="course_schedules")
    schedule_name = models.CharField(max_length=255, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=50, default="active")
    class Meta:
        db_table = "course_schedules"

class ScheduleDay(TimeStampedModel):
    course_schedule = models.ForeignKey("academics.CourseSchedule", on_delete=models.CASCADE, related_name="days")
    day_of_week = models.PositiveSmallIntegerField()
    class Meta:
        db_table = "schedule_days"
        unique_together = [("course_schedule", "day_of_week")]
