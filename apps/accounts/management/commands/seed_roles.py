from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils.text import slugify


DEFAULT_ROLES = {
    "SysAdmin": [
        ("manage_system", "Can manage system"),
        ("view_all_reports", "Can view all reports"),
    ],
    "Administrator": [
        ("manage_school", "Can manage school settings"),
        ("manage_users", "Can manage users"),
    ],
    "Training Manager": [
        ("approve_spr", "Can approve SPR"),
        ("manage_courses", "Can manage courses"),
    ],
    "Registrar": [
        ("publish_spr", "Can publish SPR"),
        ("manage_enrollments", "Can manage enrollments"),
    ],
    "Instructor": [
        ("grade_students", "Can grade students"),
        ("manage_assessments", "Can manage assessments"),
    ],
    "Accountant": [
        ("view_finance", "Can view finance records"),
        ("process_payments", "Can process payments"),
    ],
    "Cashier": [
        ("accept_payments", "Can accept payments"),
    ],
    "Marketing": [
        ("manage_enquiries", "Can manage enquiries"),
    ],
    "Receptionist": [
        ("handle_reception", "Can handle reception tasks"),
    ],
    "Student": [
        ("view_own_records", "Can view own records"),
        ("request_services", "Can request services"),
    ],
}


class Command(BaseCommand):
    help = "Seed default roles and permissions"

    def handle(self, *args, **options):
        # Use the project's accounts.Permission/Role/RolePermission models
        PermissionModel = apps.get_model("accounts", "Permission")
        RoleModel = apps.get_model("accounts", "Role")
        RolePermModel = apps.get_model("accounts", "RolePermission")

        tenant_model = None
        try:
            tenant_model = apps.get_model("saas", "Tenant")
        except LookupError:
            tenant_model = None

        system_tenant = None
        if tenant_model is not None:
            system_tenant = tenant_model.objects.first()

        created = []
        for role_name, perms in DEFAULT_ROLES.items():
            role_code = slugify(role_name)
            role_obj, _ = RoleModel.objects.get_or_create(name=role_name, code=role_code, defaults={"is_system_role": True, "tenant": system_tenant})

            for codename, description in perms:
                perm_code = codename
                module = "core"
                action = codename
                perm_obj, pcreated = PermissionModel.objects.get_or_create(code=perm_code, defaults={"module": module, "action": action, "description": description})
                if pcreated:
                    created.append(perm_code)

                # create RolePermission link
                RolePermModel.objects.get_or_create(role=role_obj, permission=perm_obj)

        self.stdout.write(self.style.SUCCESS("Seeded default accounts permissions and roles."))
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created permissions: {', '.join(created)}"))
