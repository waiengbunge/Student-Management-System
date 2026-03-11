from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase
from apps.notifications.services import NotificationService


class NotificationServiceTests(SimpleTestCase):
    @patch('apps.notifications.services.Notification')
    @patch('apps.notifications.services.NotificationLog')
    def test_send_notification_marks_sent_and_logs(self, mock_log, mock_notification):
        n = MagicMock()
        mock_notification.objects.get.return_value = n

        result = NotificationService.send_notification(1)

        self.assertTrue(result)
        mock_notification.objects.get.assert_called_once_with(pk=1)
        self.assertEqual(n.status, 'sent')
        mock_log.objects.create.assert_called()

    @patch('apps.notifications.services.Notification')
    @patch('apps.notifications.services.NotificationLog')
    def test_mark_as_read_updates_and_logs(self, mock_log, mock_notification):
        n = MagicMock()
        mock_notification.objects.get.return_value = n

        result = NotificationService.mark_as_read(2, user_id=5)

        self.assertTrue(result)
        self.assertEqual(n.status, 'read')
        mock_log.objects.create.assert_called()

    @patch('apps.notifications.services.Notification')
    def test_log_notification_creates_log(self, mock_notification):
        n = MagicMock()
        mock_notification.objects.get.return_value = n
        mock_log = MagicMock()
        with patch('apps.notifications.services.NotificationLog') as mock_log_class:
            mock_log_class.objects.create.return_value = mock_log
            nl = NotificationService.log_notification(3, 'failed', 'error')
            mock_log_class.objects.create.assert_called_once()
            self.assertIsNotNone(nl)
