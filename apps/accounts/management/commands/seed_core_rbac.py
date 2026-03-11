from django.core.management.base import BaseCommand
from apps.accounts.models import Role, Permission, RolePermission


class Command(BaseCommand):
    help = 'Seed core roles and permissions used by the system.'

    def handle(self, *args, **options):
        perms = [
            ('accounts', 'user.view', 'accounts.user.view'),
            ('accounts', 'user.create', 'accounts.user.create'),
            ('accounts', 'user.update', 'accounts.user.update'),
            ('accounts', 'user.delete', 'accounts.user.delete'),
            ('accounts', 'role.manage', 'accounts.role.manage'),
            ('students', 'profile.manage', 'students.profile.manage'),
            ('students', 'profile.view', 'students.profile.view'),
        ]

        for module, action, code in perms:
            perm, created = Permission.objects.get_or_create(module=module, action=action, code=code)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created permission {code}'))

        # create a SYSTEM_ADMIN role placeholder
        role, created = Role.objects.get_or_create(code='SYSTEM_ADMIN', defaults={'name': 'System Administrator', 'is_system_role': True})
        if created:
            self.stdout.write(self.style.SUCCESS('Created role SYSTEM_ADMIN'))

        # create a Registrar role
        registrar, rcreated = Role.objects.get_or_create(code='REGISTRAR', defaults={'name': 'Registrar'})
        if rcreated:
            self.stdout.write(self.style.SUCCESS('Created role REGISTRAR'))

        # attach a couple permissions to registrar if present
        try:
            p = Permission.objects.get(code='students.profile.view')
            RolePermission.objects.get_or_create(role=registrar, permission=p)
        except Permission.DoesNotExist:
            pass

        self.stdout.write(self.style.SUCCESS('Core RBAC seed complete.'))
