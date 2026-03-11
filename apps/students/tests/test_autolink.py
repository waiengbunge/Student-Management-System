from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.saas.models import Tenant
from apps.accounts.models import Role, UserRole
from apps.students.models import StudentProfile


class StudentAutoLinkTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='T', slug='t')
        User = get_user_model()
        self.user = User.objects.create_user(email='s1@example.com', password='pwd', username='s1', tenant=self.tenant)
        self.role = Role.objects.create(tenant=self.tenant, name='Student', code='STUDENT')

    def test_userrole_assignment_creates_student_profile(self):
        # assign student role
        ur = UserRole.objects.create(user=self.user, role=self.role)
        # StudentProfile should be auto-created by signal
        sp = StudentProfile.objects.filter(user=self.user).first()
        self.assertIsNotNone(sp)
        self.assertEqual(sp.tenant, self.tenant)
