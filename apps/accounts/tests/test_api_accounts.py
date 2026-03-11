from django.test import TestCase
from rest_framework.test import APIClient
from apps.saas.models import Tenant, Campus
from apps.accounts.models import User, Role, Permission, RolePermission, UserRole


class AccountApiTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='TestTenant', slug='testtenant')
        self.campus = Campus.objects.create(tenant=self.tenant, name='Main', code='MAIN')
        self.admin = User.objects.create_superuser(email='admin@example.com', password='TestPass123', username='admin', tenant=self.tenant)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_list_users(self):
        resp = self.client.get('/api/v1/accounts/users/')
        self.assertEqual(resp.status_code, 200)

    def test_permission_enforced_for_non_superuser(self):
        # create a regular user without permissions
        user = User.objects.create_user(email='regular@example.com', password='Pwd12345', username='regular', tenant=self.tenant)
        self.client.force_authenticate(user)
        resp = self.client.get('/api/v1/accounts/users/')
        # should be forbidden because user has no role/permission
        self.assertEqual(resp.status_code, 403)

        # grant permission via role
        perm = Permission.objects.create(module='accounts', action='manage', code='accounts.user.manage')
        role = Role.objects.create(name='Registrar', code='registrar', tenant=self.tenant)
        RolePermission.objects.create(role=role, permission=perm)
        UserRole.objects.create(user=user, role=role)

        # now the user should have access
        resp2 = self.client.get('/api/v1/accounts/users/')
        self.assertIn(resp2.status_code, (200, 204))

    def test_create_user(self):
        payload = {
            'tenant': self.tenant.id,
            'username': 'newuser',
            'email': 'user1@example.com',
            'password': 'pass1234'
        }
        resp = self.client.post('/api/v1/accounts/users/', payload)
        self.assertIn(resp.status_code, (200, 201))
