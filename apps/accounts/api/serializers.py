from rest_framework import serializers
from apps.accounts.models import User, Role, Permission, UserRole, ApiKey, UserProfile
from django.utils import timezone
import secrets
import hashlib


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "tenant", "name", "code", "is_system_role"]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "module", "action", "code", "description"]


class UserSerializer(serializers.ModelSerializer):
    primary_role = RoleSerializer(read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    profile = serializers.DictField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "tenant",
            "campus",
            "username",
            "email",
            "phone",
            "is_active",
            "is_staff",
            "is_superuser",
            "primary_role",
            "password",
        ]
        read_only_fields = ["is_superuser"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        profile_data = validated_data.pop('profile', None)
        # ensure tenant scoping: if request provided and user is not superuser, enforce tenant
        request = self.context.get('request')
        if request and not getattr(request.user, 'is_superuser', False):
            validated_data['tenant'] = getattr(request.user, 'tenant')

        # Use manager to create user correctly (handles hashing and defaults)
        email = validated_data.pop('email', None)
        username = validated_data.pop('username', None)
        if email is None:
            raise serializers.ValidationError('Email is required')
        extra = validated_data
        if username is not None:
            extra['username'] = username
        user = User.objects.create_user(email=email, password=password or None, **extra)
        # create profile if provided
        if profile_data:
            try:
                UserProfile.objects.create(user=user, **profile_data)
            except Exception:
                # avoid failing creation for simple profile issues
                pass
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        profile_data = validated_data.pop('profile', None)
        request = self.context.get('request')
        # Prevent changing tenant by non-superusers
        if request and not getattr(request.user, 'is_superuser', False):
            validated_data.pop('tenant', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        # update or create profile
        if profile_data is not None:
            try:
                profile, _ = UserProfile.objects.get_or_create(user=instance)
                for k, v in profile_data.items():
                    setattr(profile, k, v)
                profile.save()
            except Exception:
                pass
        return instance

    def validate(self, data):
        request = self.context.get('request')
        if request and not getattr(request.user, 'is_superuser', False):
            # ensure tenant matches
            tenant = data.get('tenant') or getattr(request.user, 'tenant', None)
            if tenant and tenant != getattr(request.user, 'tenant', None):
                raise serializers.ValidationError('Cannot create or modify user outside your tenant')
        # ensure unique username/email within tenant
        tenant = data.get('tenant') or (request.user.tenant if request and hasattr(request.user, 'tenant') else None)
        email = data.get('email')
        username = data.get('username')
        if tenant and email:
            qs = User.objects.filter(tenant=tenant, email=email)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError('A user with this email already exists in your tenant')
        if tenant and username:
            qs2 = User.objects.filter(tenant=tenant, username=username)
            if self.instance:
                qs2 = qs2.exclude(pk=self.instance.pk)
            if qs2.exists():
                raise serializers.ValidationError('A user with this username already exists in your tenant')
        return data


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ["id", "user", "role", "campus", "department", "starts_at", "ends_at"]

    def create(self, validated_data):
        # Ensure single-role enforcement happens in model.save(); just create
        return super().create(validated_data)

    def validate(self, data):
        # Prevent assigning roles across tenants by non-superusers
        request = self.context.get('request')
        if request and not getattr(request.user, 'is_superuser', False):
            # role tenant must match request.user.tenant if role has tenant
            role = data.get('role')
            if role and getattr(role, 'tenant', None) and role.tenant != getattr(request.user, 'tenant', None):
                raise serializers.ValidationError('Cannot assign a role from another tenant')
        return data


class ApiKeySerializer(serializers.ModelSerializer):
    # Plain token will be returned only at creation
    token = serializers.CharField(read_only=True)

    class Meta:
        model = ApiKey
        fields = ["id", "tenant", "user", "name", "key_prefix", "scopes_json", "last_used_at", "expires_at", "token"]
        read_only_fields = ["key_prefix", "last_used_at"]

    def create(self, validated_data):
        # generate a random key and store its hash
        token = secrets.token_urlsafe(32)
        prefix = token[:8]
        key_hash = hashlib.sha256(token.encode()).hexdigest()
        validated_data['key_prefix'] = prefix
        validated_data['key_hash'] = key_hash
        request = self.context.get('request')
        # restrict tenant for non-superusers
        if request and not getattr(request.user, 'is_superuser', False):
            validated_data['tenant'] = getattr(request.user, 'tenant')

        obj = super().create(validated_data)
        # attach plain token to the instance so it can be returned in representation
        setattr(obj, '_plain_token', token)
        return obj

    def validate(self, data):
        request = self.context.get('request')
        if request and not getattr(request.user, 'is_superuser', False):
            tenant = data.get('tenant') or getattr(request.user, 'tenant', None)
            if tenant and tenant != getattr(request.user, 'tenant', None):
                raise serializers.ValidationError('Cannot create ApiKey for a different tenant')
        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        token = getattr(instance, '_plain_token', None)
        if token:
            data['token'] = token
        return data


class PersonalTokenSerializer(serializers.ModelSerializer):
    """Serializer for self-service personal token management."""

    # Returned only at creation
    token = serializers.CharField(read_only=True)
    # days until expiry (write-only input)
    expires_in_days = serializers.IntegerField(write_only=True, required=False, min_value=1)

    class Meta:
        model = ApiKey
        fields = ['id', 'name', 'key_prefix', 'last_used_at', 'expires_at', 'created_at', 'token', 'expires_in_days']
        read_only_fields = ['key_prefix', 'last_used_at', 'expires_at', 'created_at']

    def create(self, validated_data):
        import datetime
        expires_in_days = validated_data.pop('expires_in_days', None)
        request = self.context['request']
        token = secrets.token_urlsafe(32)
        prefix = token[:8]
        key_hash = hashlib.sha256(token.encode()).hexdigest()
        expires_at = None
        if expires_in_days:
            expires_at = timezone.now() + datetime.timedelta(days=expires_in_days)
        obj = ApiKey.objects.create(
            tenant=request.user.tenant,
            user=request.user,
            name=validated_data['name'],
            key_prefix=prefix,
            key_hash=key_hash,
            expires_at=expires_at,
            is_active=True,
        )
        setattr(obj, '_plain_token', token)
        return obj

    def to_representation(self, instance):
        data = super().to_representation(instance)
        token = getattr(instance, '_plain_token', None)
        if token:
            data['token'] = token
        return data
