from django.test import TestCase
from rest_framework.test import APIClient
from apps.saas.models import Tenant, Campus
from apps.accounts.models import User, ApiKey, Role, Permission, RolePermission, UserRole


class ApiKeyAndPasswordTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='KeyTenant', slug='keytenant')
        self.campus = Campus.objects.create(tenant=self.tenant, name='Main', code='MAIN')
        self.admin = User.objects.create_superuser(email='admin2@example.com', password='AdminPass123', username='admin2', tenant=self.tenant)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_change_password_endpoint(self):
        # create a regular user
        u = User.objects.create_user(email='bob@example.com', password='OldPass1', username='bob', tenant=self.tenant)
        resp = self.client.post(f'/api/v1/accounts/users/{u.pk}/change-password/', {'password': 'NewPass123'})
        self.assertIn(resp.status_code, (200, 204))
        # verify password changed
        u.refresh_from_db()
        self.assertTrue(u.check_password('NewPass123'))

    def test_apikey_create_and_list_and_delete(self):
        payload = {
            'tenant': self.tenant.id,
            'user': self.admin.id,
            'name': 'CI Key',
            'scopes_json': {'scope': 'all'}
        }
        # create
        resp = self.client.post('/api/v1/accounts/api-keys/', payload)
        self.assertIn(resp.status_code, (200, 201))
        data = resp.json()
        self.assertIn('token', data)
        key_id = data.get('id')
        # list
        resp2 = self.client.get('/api/v1/accounts/api-keys/')
        self.assertEqual(resp2.status_code, 200)
        # delete
        resp3 = self.client.delete(f'/api/v1/accounts/api-keys/{key_id}/')
        self.assertIn(resp3.status_code, (200, 204, 202))
