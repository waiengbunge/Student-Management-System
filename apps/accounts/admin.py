from django.contrib import admin
from . import models
from django import forms
from django.shortcuts import get_object_or_404


@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "tenant", "is_system_role")
    search_fields = ("name", "code")


@admin.register(models.Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("code", "module", "action")
    search_fields = ("code", "module", "action")


@admin.register(models.RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "permission")
    search_fields = ("role__name", "permission__code")


@admin.register(models.UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "campus", "department", "starts_at", "ends_at")
    search_fields = ("user__email", "role__name")


@admin.register(models.UserPermissionOverride)
class UserPermissionOverrideAdmin(admin.ModelAdmin):
    list_display = ("user", "permission", "effect")
    search_fields = ("user__email", "permission__code")


class UserAdminForm(forms.ModelForm):
    role = forms.ModelChoiceField(queryset=models.Role.objects.all(), required=False)

    class Meta:
        model = models.User
        fields = ('email', 'username', 'tenant', 'is_staff', 'is_active')


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    list_display = ("email", "username", "tenant", "is_staff", "is_active", "primary_role_display")
    search_fields = ("email", "username")
    readonly_fields = ()

    def primary_role_display(self, obj):
        pr = getattr(obj, 'primary_role', None)
        return pr.name if pr else ''
    primary_role_display.short_description = 'Role'

    def save_model(self, request, obj, form, change):
        # Save user first
        super().save_model(request, obj, form, change)
        # Assign role if provided
        role = form.cleaned_data.get('role')
        if role:
            try:
                # remove other roles and assign this one
                from apps.accounts.models import UserRole
                UserRole.objects.filter(user=obj).delete()
                UserRole.objects.create(user=obj, role=role)
            except Exception:
                pass


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name")


@admin.register(models.ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "user", "last_used_at")


@admin.register(models.LoginSession)
class LoginSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "session_token", "logged_in_at", "expires_at")

