from django.test import TestCase
from apps.saas.models import Tenant
from apps.accounts.models import User, UserRole, Role
from apps.common.models import AuditLog


class AuditSignalTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='AuditTenant', slug='audittenant')

    def test_user_create_generates_audit(self):
        u = User.objects.create_user(email='aud@example.com', password='pwd1234', username='aud', tenant=self.tenant)
        # an AuditLog entry should be created
        self.assertTrue(AuditLog.objects.filter(table_name='users', record_pk=str(u.pk)).exists())

    def test_userrole_assign_generates_audit(self):
        u = User.objects.create_user(email='aud2@example.com', password='pwd1234', username='aud2', tenant=self.tenant)
        r = Role.objects.create(name='RoleA', code='rolea', tenant=self.tenant)
        ur = UserRole.objects.create(user=u, role=r)
        self.assertTrue(AuditLog.objects.filter(table_name='user_roles', record_pk=str(ur.pk)).exists())
