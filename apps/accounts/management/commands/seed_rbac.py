from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

class Command(BaseCommand):
    help = 'Seed standard Roles, Permissions and sample users for RBAC testing'

    def handle(self, *args, **options):
        from apps.saas.models import Tenant
        from apps.accounts.models import Role, Permission, RolePermission, UserRole

        User = get_user_model()

        tenant = Tenant.objects.first()
        if tenant is None:
            tenant = Tenant.objects.create(name='System', slug='system')
            self.stdout.write(self.style.SUCCESS('Created tenant `System`'))

        roles = [
            ('SYSTEM_ADMIN', 'System Administrator'),
            ('MANAGING_DIRECTOR', 'Managing Director'),
            ('TRAINING_MANAGER', 'Training Manager'),
            ('REGISTRAR', 'Registrar'),
            ('INSTRUCTOR', 'Instructor'),
            ('ACCOUNTANT', 'Accountant'),
            ('CASHIER', 'Cashier'),
            ('RECEPTIONIST', 'Receptionist'),
            ('MARKETING_MANAGER', 'Marketing Manager'),
            ('STUDENT', 'Student'),
        ]

        permissions = [
            ('enrollment.manage', 'enrollment', 'manage'),
            ('enrollment.view', 'enrollment', 'view'),
            ('scheduling.manage', 'scheduling', 'manage'),
            ('attendance.manage', 'attendance', 'manage'),
            ('assessment.manage', 'assessment', 'manage'),
            ('spr.approve', 'spr', 'approve'),
            ('finance.manage', 'finance', 'manage'),
            ('requests.manage', 'requests', 'manage'),
            ('reports.view', 'reports', 'view'),
        ]

        role_map = {}
        with transaction.atomic():
            for code, name in roles:
                r, created = Role.objects.get_or_create(tenant=tenant, code=code, defaults={'name': name, 'is_system_role': True})
                role_map[code] = r
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created role: {code}'))

            perm_map = {}
            for code, module, action in permissions:
                p, created = Permission.objects.get_or_create(code=code, defaults={'module': module, 'action': action, 'description': ''})
                perm_map[code] = p
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created permission: {code}'))

            # Map permissions to roles (approximate mapping)
            mapping = {
                'REGISTRAR': ['enrollment.manage', 'enrollment.view', 'reports.view'],
                'TRAINING_MANAGER': ['scheduling.manage', 'enrollment.manage', 'reports.view', 'finance.manage'],
                'RECEPTIONIST': ['enrollment.manage', 'requests.manage'],
                'INSTRUCTOR': ['attendance.manage', 'assessment.manage', 'spr.approve'],
                'ACCOUNTANT': ['finance.manage', 'reports.view'],
                'CASHIER': ['finance.manage'],
                'MARKETING_MANAGER': ['reports.view'],
                'MANAGING_DIRECTOR': ['reports.view', 'finance.manage'],
                'SYSTEM_ADMIN': [p for p in perm_map.keys()],
                'STUDENT': ['requests.manage'],
            }

            for role_code, perm_codes in mapping.items():
                role = role_map.get(role_code)
                if not role:
                    continue
                for pc in perm_codes:
                    perm = perm_map.get(pc)
                    if perm:
                        rp, created = RolePermission.objects.get_or_create(role=role, permission=perm)
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Assigned permission {pc} to role {role_code}'))

            # Create sample users for each role
            for role_code, role in role_map.items():
                email = f"{role_code.lower()}@example.com"
                username = role_code.lower()
                password = 'TestPass123'
                # Create superuser for system admin
                if role_code == 'SYSTEM_ADMIN':
                    if not User.objects.filter(email=email).exists():
                        try:
                            User.objects.create_superuser(email=email, password=password, username=username, tenant=tenant)
                            self.stdout.write(self.style.SUCCESS(f'Created superuser {email}'))
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'Could not create superuser {email}: {e}'))
                    user = User.objects.filter(email=email).first()
                else:
                    user, created = User.objects.get_or_create(email=email, defaults={'username': username, 'tenant': tenant})
                    if created:
                        user.set_password(password)
                        user.save()
                        self.stdout.write(self.style.SUCCESS(f'Created user {email}'))

                # assign userrole (one per user)
                try:
                    # remove existing roles for strict single-role requirement
                    UserRole.objects.filter(user=user).delete()
                except Exception:
                    pass
                try:
                    UserRole.objects.create(user=user, role=role, campus=None)
                    self.stdout.write(self.style.SUCCESS(f'Assigned role {role.code} to {user.email}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Could not assign role to {user.email}: {e}'))

        self.stdout.write(self.style.SUCCESS('RBAC seed complete. Sample credentials: email/password = <role>@example.com / TestPass123'))
