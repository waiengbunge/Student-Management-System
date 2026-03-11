from django.test import TestCase
from rest_framework.test import APIClient
from apps.saas.models import Tenant, Campus
from apps.accounts.models import User


class ExamsApiTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='ExamTenant', slug='examtenant')
        self.campus = Campus.objects.create(tenant=self.tenant, name='Main', code='MAIN')
        self.admin = User.objects.create_superuser(email='examadmin@example.com', password='Pass1234', username='examadmin', tenant=self.tenant)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_create_exam(self):
        payload = {'tenant': self.tenant.id, 'title': 'Final Exam', 'description': 'End of term'}
        resp = self.client.post('/api/v1/exams/exams/', payload)
        self.assertIn(resp.status_code, (200, 201))
