from functools import wraps
from django.shortcuts import redirect
from apps.accounts.models import RolePermission
from django.http import HttpResponseForbidden


def permission_required(permission_code):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user or not user.is_authenticated:
                return redirect('login')
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            # collect roles assigned to user
            try:
                from apps.accounts.utils import has_permission_code
            except Exception:
                has_permission_code = None
            if has_permission_code and has_permission_code(user, permission_code):
                return view_func(request, *args, **kwargs)
            return redirect('dashboard')
        return _wrapped
    return decorator


def role_required(*allowed_codes):
    """Decorator factory that checks the user's primary role code (case-insensitive).

    Usage: @role_required('TRAINING_MANAGER', 'REGISTRAR')
    """
    allowed = {c.lower() for c in allowed_codes}

    def _decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user or not user.is_authenticated:
                return redirect('login')
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            pr = getattr(user, 'primary_role', None)
            code = getattr(pr, 'code', None) or getattr(pr, 'name', None)
            if code and code.lower() in allowed:
                return view_func(request, *args, **kwargs)
            # redirect to dashboard on insufficient rights
            return redirect('dashboard')
        return _wrapped
    return _decorator


# Specific role decorators for convenience
def training_manager_required(view_func):
    return role_required('TRAINING_MANAGER')(view_func)


def registrar_required(view_func):
    return role_required('REGISTRAR')(view_func)


def instructor_required(view_func):
    return role_required('INSTRUCTOR')(view_func)


def accounts_required(view_func):
    return role_required('ACCOUNTANT', 'CASHIER')(view_func)


def student_required(view_func):
    return role_required('STUDENT')(view_func)


def marketing_required(view_func):
    return role_required('MARKETING_MANAGER')(view_func)


def system_admin_required(view_func):
    return role_required('SYSTEM_ADMIN')(view_func)


def managing_director_required(view_func):
    return role_required('MANAGING_DIRECTOR')(view_func)


def receptionist_required(view_func):
    return role_required('RECEPTIONIST')(view_func)


def cashier_required(view_func):
    return role_required('CASHIER')(view_func)
