from typing import List, Optional


def get_primary_role(user):
    try:
        return getattr(user, 'primary_role', None)
    except Exception:
        try:
            ur = user.user_roles.order_by('pk').first()
            return ur.role if ur else None
        except Exception:
            return None


def get_primary_role_name(user) -> Optional[str]:
    pr = get_primary_role(user)
    return pr.name.lower() if pr else None


def get_user_roles(user) -> List:
    try:
        return [ur.role for ur in user.user_roles.select_related('role').all()]
    except Exception:
        return []


def has_any_role(user, allowed_roles) -> bool:
    if not user:
        return False
    if getattr(user, 'is_superuser', False):
        return True
    names = set()
    try:
        names.update(r.name.lower() for r in get_user_roles(user))
    except Exception:
        pass
    try:
        names.update(g.name.lower() for g in user.groups.all())
    except Exception:
        pass
    return bool(names & set(r.lower() for r in allowed_roles))


def has_permission_code(user, code: str) -> bool:
    # Superusers always allowed
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    if getattr(user, 'is_superuser', False):
        return True
    try:
        from apps.accounts.models import RolePermission
        roles = get_user_roles(user)
        if not roles:
            return False
        return RolePermission.objects.filter(role__in=roles, permission__code=code).exists()
    except Exception:
        return False
