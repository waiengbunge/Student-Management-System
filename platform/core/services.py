# Business logic services for core app
from django.utils import timezone


class OrganizationService:
    @staticmethod
    def create_organization(data):
        from platform.core.models import Organization
        return Organization.objects.create(**data)


class RoleService:
    @staticmethod
    def assign_role(user, role):
        from apps.accounts.models import UserRole
        ur = UserRole(user=user, role=role)
        ur.save()
        return ur


class PermissionService:
    @staticmethod
    def grant_permission(role, permission):
        from apps.accounts.models import RolePermission
        return RolePermission.objects.get_or_create(role=role, permission=permission)


class AuditLogService:
    @staticmethod
    def log_action(user, action, model, object_id, changes, organization):
        from apps.common.models import AuditLog
        tenant = getattr(user, 'tenant', None)
        old_values = changes.get('before') if isinstance(changes, dict) else None
        new_values = changes.get('after') if isinstance(changes, dict) else changes
        AuditLog.objects.create(
            tenant=tenant,
            user=user,
            table_name=str(model),
            record_pk=str(object_id),
            operation=str(action),
            old_values_json=old_values,
            new_values_json=new_values,
            changed_at=timezone.now(),
        )


class NotificationService:
    @staticmethod
    def send_notification(user, title, message, organization):
        from platform.core.models import Notification
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            organization=organization,
        )