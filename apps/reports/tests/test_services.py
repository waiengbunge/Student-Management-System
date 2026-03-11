from django.test import SimpleTestCase
from apps.reports.services import ReportService


class ReportServiceTests(SimpleTestCase):
    def test_generate_report_returns_metadata(self):
        r = ReportService.generate_report(1, {'a': 1}, requested_by=10)
        self.assertIn('template_id', r)
        self.assertIn('generated_at', r)

    def test_get_student_report_returns_structure(self):
        r = ReportService.get_student_report(5, template_id=2)
        self.assertEqual(r['student_profile_id'], 5)
