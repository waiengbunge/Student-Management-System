from django.contrib import admin
from . import models
from django import forms
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import csv
from django.contrib import messages
from apps.common.models import AuditLog
from django.utils.translation import gettext_lazy as _


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
    actions = ['export_selected_users', 'bulk_activate', 'bulk_deactivate', 'bulk_set_role']
    # Action form to choose a role when assigning in bulk
    class RoleActionForm(forms.Form):
        role = forms.ModelChoiceField(queryset=models.Role.objects.all(), required=False, label=_('Role'))
    action_form = RoleActionForm
    inlines = []

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

    def export_selected_users(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['id', 'email', 'username', 'tenant_id', 'is_staff', 'is_active'])
        total = 0
        for u in queryset:
            writer.writerow([u.pk, u.email, u.username, getattr(u.tenant, 'id', None), u.is_staff, u.is_active])
            total += 1
        try:
            AuditLog.objects.create(
                tenant=getattr(request.user, 'tenant', None),
                user=request.user,
                table_name='users',
                record_pk=str(total),
                operation='export_users',
                new_values_json={'exported': total},
            )
        except Exception:
            pass
        return response

    export_selected_users.short_description = 'Export selected users (CSV)'

    def bulk_activate(self, request, queryset):
        updated = queryset.update(is_active=True)
        try:
            AuditLog.objects.create(
                tenant=getattr(request.user, 'tenant', None),
                user=request.user,
                table_name='users',
                record_pk=str(updated),
                operation='bulk_activate_users',
                new_values_json={'activated': updated},
            )
        except Exception:
            pass
        self.message_user(request, _('%d users activated.') % updated, level=messages.SUCCESS)

    bulk_activate.short_description = 'Activate selected users'

    def bulk_deactivate(self, request, queryset):
        updated = queryset.update(is_active=False)
        try:
            AuditLog.objects.create(
                tenant=getattr(request.user, 'tenant', None),
                user=request.user,
                table_name='users',
                record_pk=str(updated),
                operation='bulk_deactivate_users',
                new_values_json={'deactivated': updated},
            )
        except Exception:
            pass
        self.message_user(request, _('%d users deactivated.') % updated, level=messages.SUCCESS)

    bulk_deactivate.short_description = 'Deactivate selected users'

    def bulk_set_role(self, request, queryset):
        role_id = request.POST.get('role')
        if not role_id:
            self.message_user(request, _('No role selected.'), level=messages.ERROR)
            return
        try:
            role = models.Role.objects.get(pk=role_id)
        except models.Role.DoesNotExist:
            self.message_user(request, _('Selected role does not exist.'), level=messages.ERROR)
            return
        from apps.accounts.models import UserRole
        count = 0
        for u in queryset:
            try:
                UserRole.objects.filter(user=u).delete()
                UserRole.objects.create(user=u, role=role)
                count += 1
            except Exception:
                continue
        try:
            AuditLog.objects.create(
                tenant=getattr(request.user, 'tenant', None),
                user=request.user,
                table_name='user_roles',
                record_pk=str(count),
                operation='bulk_assign_role',
                new_values_json={'role': getattr(role, 'code', None), 'assigned': count},
            )
        except Exception:
            pass
        self.message_user(request, _('%d users assigned to role %s.') % (count, getattr(role, 'name', '')), level=messages.SUCCESS)

    bulk_set_role.short_description = 'Assign selected users to role'


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name")

# add profile inline to UserAdmin for quick edits
class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    extra = 0

# attach inline dynamically to avoid import order issues
UserAdmin.inlines = [UserProfileInline]


@admin.register(models.ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "user", "last_used_at")


@admin.register(models.LoginSession)
class LoginSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "session_token", "logged_in_at", "expires_at")

