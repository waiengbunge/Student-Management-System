from rest_framework.permissions import BasePermission


class RolePermissionDRF(BasePermission):
    """DRF permission that checks RolePermission mapping.

    Views using this should set `required_permission = '<module>.<action>'`
    as a class attribute.
    """

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        # Support dynamic per-action permission resolution via view.get_required_permission
        code = None
        get_req = getattr(view, 'get_required_permission', None)
        if callable(get_req):
            try:
                code = get_req(request)
            except Exception:
                code = None
        if not code:
            code = getattr(view, 'required_permission', None)
        if not code:
            return True
        try:
            from apps.accounts.utils import has_permission_code
            return has_permission_code(user, code)
        except Exception:
            return False
