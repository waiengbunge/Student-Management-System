import hashlib

from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class ApiKeyAuthentication(BaseAuthentication):
    """
    DRF authentication class that validates Personal Access Tokens (API keys).

    Accepts the token in either of these header forms:
        Authorization: Bearer <token>
        Authorization: Token <token>

    The plain token is SHA-256 hashed and matched against ApiKey.key_hash.
    Enforces is_active and expires_at; stamps last_used_at on every successful auth.
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2:
            return None

        scheme, token = parts
        if scheme.lower() not in ('bearer', 'token'):
            return None

        return self._authenticate_token(token)

    def _authenticate_token(self, token):
        from apps.accounts.models import ApiKey

        token_hash = hashlib.sha256(token.encode()).hexdigest()

        try:
            api_key = ApiKey.objects.select_related('user').get(
                key_hash=token_hash,
                is_active=True,
            )
        except ApiKey.DoesNotExist:
            # Not a PAT — let the next authenticator (e.g. JWT) try
            return None

        if api_key.expires_at and api_key.expires_at < timezone.now():
            raise AuthenticationFailed('API key has expired.')

        if api_key.user is None:
            raise AuthenticationFailed('API key is not associated with a user.')

        # Stamp last used timestamp
        ApiKey.objects.filter(pk=api_key.pk).update(last_used_at=timezone.now())

        return (api_key.user, api_key)
