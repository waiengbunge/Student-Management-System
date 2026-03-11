from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from apps.accounts.management.commands.seed_rbac import Command as SeedCommand

class RBACSmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Seed roles and sample users
        cmd = SeedCommand()
        cmd.handle()

    def setUp(self):
        self.client = Client()
        self.User = get_user_model()

    def test_seeded_users_can_login_and_reach_dashboard(self):
        # The seed command creates sample users with known password 'TestPass123'
        users = self.User.objects.all()[:5]
        for u in users:
            login = self.client.login(username=u.email, password='TestPass123')
            self.assertTrue(login)
            r = self.client.get('/dashboard/')
            self.assertIn(r.status_code, (200, 302))

    def test_has_permission_helper(self):
        # pick a user and assert helper responses don't crash
        u = self.User.objects.first()
        from apps.accounts.utils import has_permission_code, has_any_role
        self.assertIsInstance(has_any_role(u, ['system administrator']), bool)
        self.assertIsInstance(has_permission_code(u, 'enrollment.view'), bool)
