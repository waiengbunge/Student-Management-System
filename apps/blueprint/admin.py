from django.contrib import admin
from . import models

MODEL_REGISTRY = [
    models.School,
    models.Program,
    models.Department,
    models.Staff,
    models.StaffRole,
    models.Student,
    models.Course,
    models.Classroom,
    models.AcademicSession,
    models.AcademicCalendar,
    models.Module,
    models.CourseSchedule,
    models.StudentEnrollment,
    models.AssessmentComponent,
    models.StudentAssessment,
    models.AttendanceRecord,
    models.SPR,
    models.SPRVersion,
    models.ExamSchedule,
    models.ExamPermit,
    models.FeeStructure,
    models.StudentFee,
    models.PaymentTransaction,
    models.MonthlyInstallment,
    models.StudentRequest,
    models.Enquiry,
    models.WebsiteContent,
    models.ActivityLog,
]


for m in MODEL_REGISTRY:
    try:
        admin.site.register(m)
    except Exception:
        # already registered or other admin errors
        pass
