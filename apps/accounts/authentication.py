import hashlib
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class ApiKeyAuthentication(BaseAuthentication):
    """DRF authentication class that validates personal access tokens.

    Clients pass the token in the ``Authorization`` header using either of:
        Authorization: Bearer <token>
        Authorization: Token <token>

    The token is hashed with SHA-256 and compared against the stored
    ``key_hash`` in the ``ApiKey`` model.  On success the associated user
    (``ApiKey.user``) is returned so DRF can set ``request.user``.
    """

    keyword = ("Bearer", "Token")

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2:
            return None

        scheme, token = parts
        if scheme not in self.keyword:
            return None

        return self._authenticate_token(token)

    def _authenticate_token(self, token):
        from apps.accounts.models import ApiKey

        token_hash = hashlib.sha256(token.encode()).hexdigest()
        try:
            api_key = ApiKey.objects.select_related("user").get(key_hash=token_hash)
        except ApiKey.DoesNotExist:
            raise AuthenticationFailed("Invalid or expired personal access token.")

        # Check expiry
        if api_key.expires_at and api_key.expires_at < timezone.now():
            raise AuthenticationFailed("Personal access token has expired.")

        user = api_key.user
        if user is None or not user.is_active:
            raise AuthenticationFailed("User account is inactive or removed.")

        # Record last usage without raising on failure
        try:
            ApiKey.objects.filter(pk=api_key.pk).update(last_used_at=timezone.now())
        except Exception:
            pass

        return (user, api_key)

    def authenticate_header(self, request):
        return "Bearer"
