from django.test import TestCase
from rest_framework.test import APIClient
from apps.saas.models import Tenant, Campus
from apps.accounts.models import User


class AssessmentsApiTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='AssessTenant', slug='assesstenant')
        self.campus = Campus.objects.create(tenant=self.tenant, name='Main', code='MAIN')
        self.admin = User.objects.create_superuser(email='assessadmin@example.com', password='Pass1234', username='assessadmin', tenant=self.tenant)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_create_assessment(self):
        payload = {'tenant': self.tenant.id, 'name': 'Midterm Exam', 'assessment_type': 'exam'}
        resp = self.client.post('/api/v1/assessments/assessments/', payload)
        self.assertIn(resp.status_code, (200, 201))

*** End Patch