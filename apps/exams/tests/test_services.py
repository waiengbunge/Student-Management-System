from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase
from apps.exams.services import ExamService


class ExamServiceTests(SimpleTestCase):
    @patch('apps.exams.services.ExamSession')
    def test_schedule_exam_updates(self, mock_session):
        es = MagicMock()
        mock_session.objects.get.return_value = es
        res = ExamService.schedule_exam(1, course_id=3, class_id=4)
        mock_session.objects.get.assert_called_once_with(pk=1)
        self.assertEqual(res, es)

    @patch('apps.exams.services.StudentExamResult')
    def test_record_exam_attendance_get_or_create(self, mock_result):
        mock_result.objects.get_or_create.return_value = (MagicMock(), True)
        r = ExamService.record_exam_attendance(1, 2, True)
        mock_result.objects.get_or_create.assert_called_once()
        self.assertIsNotNone(r)

    @patch('apps.exams.services.StudentExamResult')
    def test_publish_exam_results_counts(self, mock_result):
        m1 = MagicMock()
        m2 = MagicMock()
        mock_qs = [m1, m2]
        mock_result.objects.filter.return_value = mock_qs
        count = ExamService.publish_exam_results(1)
        self.assertEqual(count, 2)
