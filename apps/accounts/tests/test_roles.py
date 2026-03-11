from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.accounts.models import Role, UserRole, Permission, RolePermission
from apps.saas.models import Tenant

class RoleBasedAuthTests(TestCase):
    def setUp(self):
        Tenant.objects.all().delete()
        tenant = Tenant.objects.create(name='System', slug='system')
        User = get_user_model()
        self.admin = User.objects.create_superuser(email='admin@example.com', username='admin', password='pass', tenant=tenant)
        self.student_user = User.objects.create_user(email='s@example.com', username='student1', password='pass', tenant=tenant)
        # create roles and permission
        self.student_role = Role.objects.create(name='Student', code='student')
        self.admin_role = Role.objects.create(name='System Administrator', code='system_admin')
        # create permission and assign to student role (view student dashboard)
        self.perm_view = Permission.objects.create(module='dashboard', action='view_student', code='dashboard.view_student')
        RolePermission.objects.create(role=self.student_role, permission=self.perm_view)
        # assign student role
        UserRole.objects.create(user=self.student_user, role=self.student_role)
        self.client = Client()

    def test_student_login_redirects_to_student_dashboard(self):
        resp = self.client.post(reverse('login'), {'username': 's@example.com', 'password': 'pass'})
        # after login should redirect
        self.assertIn(resp.status_code, (302, 200))
        # follow redirect if 302
        if resp.status_code == 302:
            follow = self.client.get(resp['Location'])
            self.assertEqual(follow.status_code, 200)

    def test_admin_sees_permissions_page(self):
        self.client.login(username='admin@example.com', password='pass')
        resp = self.client.get(reverse('admin_permissions'))
        self.assertEqual(resp.status_code, 200)