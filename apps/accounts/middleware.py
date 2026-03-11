from django.utils.deprecation import MiddlewareMixin


class RoleMiddleware(MiddlewareMixin):
    """Attach primary role and role name to the request for quick access in views/templates.

    Sets `request.primary_role` (Role or None) and `request.role_name` (lowercase string or None).
    """

    def process_request(self, request):
        request.primary_role = None
        request.role_name = None
        user = getattr(request, 'user', None)
        if user and getattr(user, 'is_authenticated', False):
            try:
                pr = getattr(user, 'primary_role', None)
                request.primary_role = pr
                request.role_name = pr.name.lower() if pr else None
            except Exception:
                request.primary_role = None
                request.role_name = None
        return None
