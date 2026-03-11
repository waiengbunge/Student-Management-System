# Business logic services for core app

from django.utils import timezone


class OrganizationService:
    @staticmethod
    def create_organization(data):
        """Create and return a new Organization instance from the provided data dict."""
        from platform.core.models import Organization
        return Organization.objects.create(
            name=data.get('name', ''),
            type=data.get('type', 'school'),
            address=data.get('address', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
        )


class RoleService:
    @staticmethod
    def assign_role(user, role):
        """Assign *role* to *user*, replacing any existing role (single-role policy).

        Returns the newly created UserRole instance.
        """
        from apps.accounts.models import UserRole
        user_role = UserRole(user=user, role=role)
        user_role.save()
        return user_role


class PermissionService:
    @staticmethod
    def grant_permission(role, permission):
        """Grant *permission* to *role*.

        Idempotent: returns the existing RolePermission if the grant already exists,
        otherwise creates a new one. Returns a ``(role_permission, created)`` tuple.
        """
        from apps.accounts.models import RolePermission
        return RolePermission.objects.get_or_create(role=role, permission=permission)


class AuditLogService:
    @staticmethod
    def log_action(user, action, model, object_id, changes, organization):
        """Record an audit-log entry.

        Parameters
        ----------
        user        : accounts.User – the actor (may be ``None`` for system actions)
        action      : str – operation name, e.g. "CREATE", "UPDATE", "DELETE"
        model       : str – DB table name or model label being audited
        object_id   : str | int – primary key of the affected record
        changes     : dict – ``{'before': {...}, 'after': {...}}`` or a flat diff dict
        organization: core.Organization – owning organization (used for context only)
        """
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
        """Create an in-app notification for *user* and return the saved instance."""
        from platform.core.models import Notification
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            organization=organization,
        )