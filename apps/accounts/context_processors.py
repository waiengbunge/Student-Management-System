from django.utils.functional import SimpleLazyObject


def _compute_user_is_admin(user):
    try:
        if not user or user.is_anonymous:
            return False
        group_names = set(g.name.lower() for g in user.groups.all())
        # consider roles as admin if user has admin-like roles
        role_names = set()
        try:
            role_names = set(r.role.name.lower() for r in user.user_roles.all())
        except Exception:
            role_names = set()
        admin_like = bool(user.is_staff or user.is_superuser or 'admin' in group_names or 'system administrator' in role_names or 'managing director' in role_names)
        return admin_like
    except Exception:
        return False


def user_is_admin(request):
    def _compute():
        is_admin = _compute_user_is_admin(request.user)
        role_name = None
        try:
            pr = getattr(request.user, 'primary_role', None)
            role_name = pr.name.lower() if pr else None
        except Exception:
            role_name = None
        is_admin_role = role_name in ('system administrator', 'managing director')
        return {'user_is_admin': is_admin, 'role_name': role_name, 'is_admin_role': is_admin_role}

    return SimpleLazyObject(lambda: _compute())
