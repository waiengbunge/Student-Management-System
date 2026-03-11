from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from apps.accounts.models import User, UserRole
from apps.common.models import AuditLog


def _log_audit(instance, operation, user=None, changed_at=None):
    try:
        AuditLog.objects.create(
            tenant=getattr(instance, 'tenant', None) or getattr(instance, 'user', None) and getattr(getattr(instance, 'user'), 'tenant', None),
            user=user,
            table_name=instance._meta.db_table,
            record_pk=str(getattr(instance, 'pk', '')),
            operation=operation,
            old_values_json=None,
            new_values_json=None,
            changed_at=changed_at or timezone.now(),
        )
    except Exception:
        # Avoid raising in signal handlers
        pass


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    _log_audit(instance, 'create' if created else 'update', user=getattr(instance, 'created_by', None))


@receiver(post_delete, sender=User)
def user_post_delete(sender, instance, **kwargs):
    _log_audit(instance, 'delete')


@receiver(post_save, sender=UserRole)
def userrole_post_save(sender, instance, created, **kwargs):
    _log_audit(instance, 'assign' if created else 'update', user=getattr(instance, 'user', None))
    # Auto-link: if a role that indicates a student is assigned, ensure a StudentProfile exists
    try:
        if created and instance.role and getattr(instance.role, 'code', ''):
            role_code = instance.role.code.lower()
            if 'student' in role_code or role_code in ('learner', 'student_role'):
                # import here to avoid circular import
                from apps.students.models import StudentProfile
                from apps.students.services import generate_student_number
                # create StudentProfile if not exists
                user = instance.user
                if user:
                    tenant = getattr(user, 'tenant', None)
                    campus = getattr(instance, 'campus', getattr(user, 'campus', None))
                    student_number = generate_student_number(tenant, campus, user)
                    sp, sp_created = StudentProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            'tenant': tenant,
                            'campus': campus,
                            'student_number': student_number,
                        },
                    )
                    # optionally, write an audit entry for creation
                    if sp_created:
                        _log_audit(sp, 'create', user=user)
    except Exception:
        pass


@receiver(post_delete, sender=UserRole)
def userrole_post_delete(sender, instance, **kwargs):
    _log_audit(instance, 'unassign', user=getattr(instance, 'user', None))
