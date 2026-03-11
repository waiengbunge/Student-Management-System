RBAC Overview

- Users-first: all people are `User` records. Roles are assigned by admins.
- Single role per user: the system enforces one active `UserRole` per user.
- Role -> Permission mapping: `RolePermission` links roles to permission codes.
- Enforcement:
  - Templates and views should use `apps.accounts.utils.get_primary_role()` or `user.primary_role`.
  - Function views use `apps.accounts.decorators.permission_required`.
  - DRF viewsets should include `apps.accounts.drf_permissions.RolePermissionDRF` and set `required_permission`.

Admin workflow

- Create `Role` and `Permission` entries via Django admin (`Users`, `Roles`, `Permissions`).
- Assign a single role to a user via the User admin `Role` field or the `UserRole` admin.
- To grant a permission to a role, use the `RolePermission` admin.

Developer notes

- Use `apps.accounts.utils.has_any_role(user, roles)` for role membership checks.
- Use `apps.accounts.utils.has_permission_code(user, code)` for permission checks.
- Prefer `user.primary_role` in templates for display.
- Seed roles/permissions using `manage.py seed_rbac` (existing management command).
