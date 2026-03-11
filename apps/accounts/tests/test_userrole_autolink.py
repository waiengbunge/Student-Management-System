from django.test import TestCase
from apps.saas.models import Tenant
from apps.accounts.models import User, Role, UserRole
from apps.students.models import StudentProfile


class UserRoleAutoLinkTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='LinkTenant', slug='linktenant')

    def test_assign_student_role_creates_student_profile(self):
        u = User.objects.create_user(email='stu@example.com', password='pwd1234', username='stu1', tenant=self.tenant)
        r = Role.objects.create(name='Student', code='STUDENT', tenant=self.tenant)
        # assign role
        ur = UserRole.objects.create(user=u, role=r)
        # StudentProfile should be created automatically
        sp = StudentProfile.objects.filter(user=u).first()
        self.assertIsNotNone(sp)
        # generated student number should match our service format
        self.assertTrue(sp.student_number.startswith(f"ST-{self.tenant.id}-"))
