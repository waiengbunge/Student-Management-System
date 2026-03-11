from django import template
from django.apps import apps

register = template.Library()


@register.simple_tag(takes_context=True)
def has_permission(context, perm_code):
    request = context.get("request")
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False):
        return True

    try:
        Permission = apps.get_model("accounts", "Permission")
        RolePermission = apps.get_model("accounts", "RolePermission")
    except LookupError:
        return False

    # collect permission ids matching code
    perms = Permission.objects.filter(code=perm_code)
    if not perms.exists():
        return False

    # use utility helper to check permission
    try:
        from apps.accounts.utils import has_permission_code
        return has_permission_code(user, perm_code)
    except Exception:
        return False
