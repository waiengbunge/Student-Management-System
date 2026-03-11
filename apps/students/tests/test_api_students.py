from django.test import TestCase
from rest_framework.test import APIClient
from apps.saas.models import Tenant, Campus
from apps.accounts.models import User, Role, Permission, RolePermission, UserRole
from apps.students.models import StudentProfile


class StudentApiTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='StudTenant', slug='studtenant')
        self.campus = Campus.objects.create(tenant=self.tenant, name='Main', code='MAIN')
        self.user = User.objects.create_user(email='student@example.com', password='StudPass123', username='student', tenant=self.tenant)
        self.admin = User.objects.create_superuser(email='admin2@example.com', password='AdminPass123', username='admin2', tenant=self.tenant)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_create_student_profile(self):
        payload = {
            'tenant': self.tenant.id,
            'campus': self.campus.id,
            'user': self.user.id,
            'student_number': 'S12345'
        }
        resp = self.client.post('/api/v1/students/profiles/', payload)
        self.assertIn(resp.status_code, (200, 201))

    def test_list_student_profiles(self):
        resp = self.client.get('/api/v1/students/profiles/')
        self.assertEqual(resp.status_code, 200)

    def test_permission_enforced_for_non_superuser(self):
        # regular user should be forbidden by default
        self.client.force_authenticate(self.user)
        resp = self.client.get('/api/v1/students/profiles/')
        self.assertEqual(resp.status_code, 403)

        # grant permission and assign role
        perm = Permission.objects.create(module='students', action='manage', code='students.profile.manage')
        role = Role.objects.create(name='Registrar', code='registrar', tenant=self.tenant)
        RolePermission.objects.create(role=role, permission=perm)
        UserRole.objects.create(user=self.user, role=role)

        resp2 = self.client.get('/api/v1/students/profiles/')
        self.assertIn(resp2.status_code, (200, 204))
