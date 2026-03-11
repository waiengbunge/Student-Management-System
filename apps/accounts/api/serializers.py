from rest_framework import serializers
from apps.accounts.models import User, Role, Permission, UserRole, ApiKey
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
        # ensure tenant scoping: if request provided and user is not superuser, enforce tenant
        request = self.context.get('request')
        if request and not getattr(request.user, 'is_superuser', False):
            validated_data['tenant'] = getattr(request.user, 'tenant')

        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        request = self.context.get('request')
        # Prevent changing tenant by non-superusers
        if request and not getattr(request.user, 'is_superuser', False):
            validated_data.pop('tenant', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def validate(self, data):
        request = self.context.get('request')
        if request and not getattr(request.user, 'is_superuser', False):
            # ensure tenant matches
            tenant = data.get('tenant') or getattr(request.user, 'tenant', None)
            if tenant and tenant != getattr(request.user, 'tenant', None):
                raise serializers.ValidationError('Cannot create or modify user outside your tenant')
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
        obj = super().create(validated_data)
        # attach plain token to the instance so it can be returned in representation
        setattr(obj, '_plain_token', token)
        return obj

    def to_representation(self, instance):
        data = super().to_representation(instance)
        token = getattr(instance, '_plain_token', None)
        if token:
            data['token'] = token
        return data
