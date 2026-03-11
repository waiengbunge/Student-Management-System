from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.accounts.models import Role, UserRole
from apps.saas.models import Tenant

class RBACDashboardTests(TestCase):
    def setUp(self):
        tenant, _ = Tenant.objects.get_or_create(name='System', slug='system')
        User = get_user_model()
        # create roles
        self.registrar_role, _ = Role.objects.get_or_create(tenant=tenant, code='REGISTRAR', defaults={'name':'Registrar'})
        # create user
        self.user = User.objects.create_user(email='test_registrar@example.com', username='test_registrar', password='pass123', tenant=tenant)
        UserRole.objects.create(user=self.user, role=self.registrar_role)
        self.client = Client()

    def test_registrar_login_redirects_to_dashboard(self):
        resp = self.client.post(reverse('login'), {'username': 'test_registrar@example.com', 'password': 'pass123'}, follow=True)
        self.assertEqual(resp.status_code, 200)
        # ensure dashboard content rendered
        self.assertIn('Registrar', resp.content.decode('utf-8') or '')
