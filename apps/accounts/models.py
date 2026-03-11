from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from apps.common.models import TimeStampedModel
# from apps.accounts.managers import UserManager  # You will need to implement a custom manager

class UserStatus(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    class Meta:
        db_table = "user_statuses"

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        # Ensure a tenant is assigned for superusers. If none exists, create a system tenant.
        if extra_fields.get('tenant') is None:
            from apps.saas.models import Tenant
            tenant = Tenant.objects.first()
            if tenant is None:
                tenant = Tenant.objects.create(name="System", slug="system")
            extra_fields['tenant'] = tenant
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    tenant = models.ForeignKey("saas.Tenant", on_delete=models.CASCADE, related_name="users")
    campus = models.ForeignKey("saas.Campus", on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    status = models.ForeignKey("accounts.UserStatus", on_delete=models.PROTECT, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login_at = models.DateTimeField(null=True, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = UserManager()
    class Meta:
        db_table = "users"
        unique_together = [("tenant", "username"), ("tenant", "email")]
    def __str__(self):
        return f"{self.email} ({self.tenant})"
    @property
    def primary_role(self):
        """Return the primary Role instance for the user (first assigned UserRole) or None."""
        try:
            ur = self.user_roles.order_by('pk').first()
            return ur.role if ur else None
        except Exception:
            return None

    def primary_role_name(self):
        r = self.primary_role
        return r.name.lower() if r else None

class UserProfile(TimeStampedModel):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=120)
    middle_name = models.CharField(max_length=120, blank=True)
    last_name = models.CharField(max_length=120)
    gender = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    photo = models.ForeignKey("common.FileUpload", on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField(blank=True)
    class Meta:
        db_table = "user_profiles"

class Role(TimeStampedModel):
    tenant = models.ForeignKey("saas.Tenant", on_delete=models.CASCADE, null=True, blank=True, related_name="roles")
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=120)
    is_system_role = models.BooleanField(default=False)
    class Meta:
        db_table = "roles"
        unique_together = [("tenant", "code")]

class Permission(TimeStampedModel):
    module = models.CharField(max_length=120)
    action = models.CharField(max_length=120)
    code = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = "permissions"

class RolePermission(TimeStampedModel):
    role = models.ForeignKey("accounts.Role", on_delete=models.CASCADE, related_name="role_permissions")
    permission = models.ForeignKey("accounts.Permission", on_delete=models.CASCADE, related_name="permission_roles")
    class Meta:
        db_table = "role_permissions"
        unique_together = [("role", "permission")]


class UserRole(TimeStampedModel):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey("accounts.Role", on_delete=models.CASCADE, related_name="user_roles")
    campus = models.ForeignKey("saas.Campus", on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey("hr.Department", on_delete=models.SET_NULL, null=True, blank=True)
    scope_type = models.CharField(max_length=50, default="tenant")
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "user_roles"
        unique_together = [("user", "role", "campus", "department")]

    def save(self, *args, **kwargs):
        # Enforce a single-role policy: remove other roles for this user before saving
        try:
            if self.pk is None and self.user_id:
                # remove existing roles for strict single-role requirement
                type(self).objects.filter(user_id=self.user_id).delete()
        except Exception:
            pass
        super().save(*args, **kwargs)

class UserPermissionOverride(TimeStampedModel):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="permission_overrides")
    permission = models.ForeignKey("accounts.Permission", on_delete=models.CASCADE, related_name="user_overrides")
    effect = models.CharField(max_length=20)  # allow / deny
    class Meta:
        db_table = "user_permission_overrides"
        unique_together = [("user", "permission")]

class LoginSession(TimeStampedModel):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="login_sessions")
    session_token = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    logged_in_at = models.DateTimeField()
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "login_sessions"

class ApiKey(TimeStampedModel):
    tenant = models.ForeignKey("saas.Tenant", on_delete=models.CASCADE, related_name="api_keys")
    user = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="api_keys")
    name = models.CharField(max_length=120)
    key_prefix = models.CharField(max_length=20)
    key_hash = models.CharField(max_length=255)
    scopes_json = models.JSONField(default=dict, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = "api_keys"
