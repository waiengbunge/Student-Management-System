from django.test import TestCase
from rest_framework.test import APIClient
from apps.saas.models import Tenant, Campus
from apps.accounts.models import User
from apps.academics.models import Program


class AcademicsApiTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='AcadTenant', slug='acadtenant')
        self.campus = Campus.objects.create(tenant=self.tenant, name='Main', code='MAIN')
        self.admin = User.objects.create_superuser(email='adminacad@example.com', password='Pass1234', username='adminacad', tenant=self.tenant)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_create_program(self):
        payload = {
            'tenant': self.tenant.id,
            'campus': self.campus.id,
            'name': 'Test Program',
            'code': 'TP01'
        }
        resp = self.client.post('/api/v1/academics/programs/', payload)
        self.assertIn(resp.status_code, (200, 201))

    def test_list_programs(self):
        Program.objects.create(tenant=self.tenant, campus=self.campus, name='P1', code='P1')
        resp = self.client.get('/api/v1/academics/programs/')
        self.assertEqual(resp.status_code, 200)
