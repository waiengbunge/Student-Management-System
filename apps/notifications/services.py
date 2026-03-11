from django.utils import timezone
from .models import Notification, NotificationLog


class NotificationService:
    """Service methods for notification workflows."""
    @staticmethod
    def send_notification(notification_id):
        try:
            n = Notification.objects.get(pk=notification_id)
        except Notification.DoesNotExist:
            return False

        # For now, we treat sending as a status update and log creation.
        n.status = 'sent'
        n.sent_at = timezone.now()
        n.save(update_fields=['status', 'sent_at'])
        NotificationLog.objects.create(notification=n, status='sent', log_message='Marked as sent')
        return True

    @staticmethod
    def mark_as_read(notification_id, user_id=None):
        try:
            n = Notification.objects.get(pk=notification_id)
        except Notification.DoesNotExist:
            return False

        n.read_at = timezone.now()
        n.status = 'read'
        n.save(update_fields=['read_at', 'status'])
        NotificationLog.objects.create(notification=n, status='read', log_message=f'Read by user {user_id}')
        return True

    @staticmethod
    def log_notification(notification_id, status, log_message=None):
        try:
            n = Notification.objects.get(pk=notification_id)
        except Notification.DoesNotExist:
            return None

        nl = NotificationLog.objects.create(notification=n, status=status, log_message=log_message or '')
        return nl
