from django.test import TestCase
from apps.saas.models import Tenant, Campus
from apps.accounts.models import User
from apps.students.models import StudentProfile, Enrollment
from apps.academics.models import Program, AcademicYear, Term, Class
from rest_framework.test import APIClient


class EnrollmentValidationTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='EnrollTenant', slug='enrolltenant')
        self.campus = Campus.objects.create(tenant=self.tenant, name='Main', code='MAIN')
        self.user = User.objects.create_user(email='s1@example.com', password='pwd', username='s1', tenant=self.tenant)
        self.student = StudentProfile.objects.create(user=self.user, tenant=self.tenant, campus=self.campus, student_number='S0001')
        self.admin = User.objects.create_superuser(email='adm@example.com', password='pwd', username='adm', tenant=self.tenant)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)
        self.program = Program.objects.create(tenant=self.tenant, campus=self.campus, name='Prog', code='P1')
        self.academic_year = AcademicYear.objects.create(tenant=self.tenant, name='2026', code='2026', start_date='2026-01-01', end_date='2026-12-31')
        self.term = Term.objects.create(tenant=self.tenant, academic_year=self.academic_year, name='Term1', code='T1', start_date='2026-01-01', end_date='2026-03-31')

    def test_prevent_duplicate_enrollment_same_term(self):
        Enrollment.objects.create(student_profile=self.student, program=self.program, academic_year=self.academic_year, term=self.term, enrollment_number='E1', enrolled_on='2026-01-05', status='active')
        payload = {
            'student_profile': self.student.id,
            'program': self.program.id,
            'academic_year': self.academic_year.id,
            'term': self.term.id,
            'enrolled_on': '2026-01-05',
        }
        resp = self.client.post('/api/v1/students/enrollments/', payload)
        self.assertEqual(resp.status_code, 400)

    def test_class_capacity_block(self):
        cls = Class.objects.create(tenant=self.tenant, campus=self.campus, program=self.program, academic_year=self.academic_year, name='C1', code='C1', capacity=1)
        # create existing enrollment in class
        other_user = User.objects.create_user(email='s2@example.com', password='pwd', username='s2', tenant=self.tenant)
        other_student = StudentProfile.objects.create(user=other_user, tenant=self.tenant, campus=self.campus, student_number='S0002')
        Enrollment.objects.create(student_profile=other_student, program=self.program, academic_year=self.academic_year, term=self.term, class_obj=cls, enrollment_number='E2', enrolled_on='2026-01-05', status='active')

        payload = {
            'student_profile': self.student.id,
            'program': self.program.id,
            'academic_year': self.academic_year.id,
            'term': self.term.id,
            'class_obj': cls.id,
            'enrolled_on': '2026-01-05',
        }
        resp = self.client.post('/api/v1/students/enrollments/', payload)
        self.assertEqual(resp.status_code, 400)
