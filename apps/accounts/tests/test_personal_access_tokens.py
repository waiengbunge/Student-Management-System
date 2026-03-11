"""Tests for Personal Access Token (PAT) authentication and self-service endpoint."""

import hashlib
import secrets
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.authentication import ApiKeyAuthentication
from apps.accounts.models import ApiKey, User
from apps.saas.models import Campus, Tenant


class ApiKeyAuthenticationTests(TestCase):
    """Unit tests for ApiKeyAuthentication."""

    def setUp(self):
        self.tenant = Tenant.objects.create(name="AuthTenant", slug="authtenant")
        self.campus = Campus.objects.create(tenant=self.tenant, name="Main", code="MAIN")
        self.user = User.objects.create_user(
            email="pat_user@example.com",
            password="Pass123!",
            username="pat_user",
            tenant=self.tenant,
        )
        self.token = secrets.token_urlsafe(32)
        self.api_key = ApiKey.objects.create(
            tenant=self.tenant,
            user=self.user,
            name="Test Token",
            key_prefix=self.token[:8],
            key_hash=hashlib.sha256(self.token.encode()).hexdigest(),
        )
        self.auth = ApiKeyAuthentication()
        self.client = APIClient()

    def _make_request(self, header_value):
        from django.test import RequestFactory
        factory = RequestFactory()
        req = factory.get("/")
        req.META["HTTP_AUTHORIZATION"] = header_value
        return req

    def test_valid_bearer_token_authenticates(self):
        req = self._make_request(f"Bearer {self.token}")
        result = self.auth.authenticate(req)
        self.assertIsNotNone(result)
        user, key = result
        self.assertEqual(user, self.user)
        self.assertEqual(key, self.api_key)

    def test_valid_token_keyword_authenticates(self):
        req = self._make_request(f"Token {self.token}")
        result = self.auth.authenticate(req)
        self.assertIsNotNone(result)
        user, _ = result
        self.assertEqual(user, self.user)

    def test_invalid_token_raises_auth_failed(self):
        from rest_framework.exceptions import AuthenticationFailed
        req = self._make_request("Bearer invalidtoken")
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(req)

    def test_no_auth_header_returns_none(self):
        req = self._make_request("")
        result = self.auth.authenticate(req)
        self.assertIsNone(result)

    def test_unknown_scheme_returns_none(self):
        req = self._make_request(f"Basic {self.token}")
        result = self.auth.authenticate(req)
        self.assertIsNone(result)

    def test_expired_token_raises_auth_failed(self):
        from rest_framework.exceptions import AuthenticationFailed
        expired_token = secrets.token_urlsafe(32)
        ApiKey.objects.create(
            tenant=self.tenant,
            user=self.user,
            name="Expired",
            key_prefix=expired_token[:8],
            key_hash=hashlib.sha256(expired_token.encode()).hexdigest(),
            expires_at=timezone.now() - timedelta(days=1),
        )
        req = self._make_request(f"Bearer {expired_token}")
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(req)

    def test_last_used_at_updated_on_success(self):
        req = self._make_request(f"Bearer {self.token}")
        self.auth.authenticate(req)
        self.api_key.refresh_from_db()
        self.assertIsNotNone(self.api_key.last_used_at)

    def test_inactive_user_raises_auth_failed(self):
        from rest_framework.exceptions import AuthenticationFailed
        self.user.is_active = False
        self.user.save()
        req = self._make_request(f"Bearer {self.token}")
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(req)


class PersonalTokenEndpointTests(TestCase):
    """Integration tests for /api/v1/accounts/me/tokens/ self-service endpoint."""

    def setUp(self):
        self.tenant = Tenant.objects.create(name="PTTenant", slug="pttenant")
        self.campus = Campus.objects.create(tenant=self.tenant, name="Main", code="PTMAIN")
        self.user = User.objects.create_user(
            email="pt_user@example.com",
            password="Pass123!",
            username="pt_user",
            tenant=self.tenant,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_personal_token(self):
        resp = self.client.post(
            "/api/v1/accounts/me/tokens/",
            {"name": "My VS Code Token"},
        )
        self.assertIn(resp.status_code, (200, 201))
        data = resp.json()
        # Plain token returned once
        self.assertIn("token", data)
        self.assertTrue(len(data["token"]) > 10)
        # key_prefix present
        self.assertIn("key_prefix", data)
        # token is not stored in plain form (hash is stored)
        api_key = ApiKey.objects.get(pk=data["id"])
        self.assertNotEqual(api_key.key_hash, data["token"])
        self.assertEqual(api_key.user, self.user)
        self.assertEqual(api_key.tenant, self.tenant)

    def test_list_only_own_tokens(self):
        # Create a token for this user
        self.client.post("/api/v1/accounts/me/tokens/", {"name": "Token A"})
        # Create a second user with their own token
        other = User.objects.create_user(
            email="other@example.com", password="Pass123!", username="other", tenant=self.tenant
        )
        raw = secrets.token_urlsafe(32)
        ApiKey.objects.create(
            tenant=self.tenant,
            user=other,
            name="Other token",
            key_prefix=raw[:8],
            key_hash=hashlib.sha256(raw.encode()).hexdigest(),
        )
        resp = self.client.get("/api/v1/accounts/me/tokens/")
        self.assertEqual(resp.status_code, 200)
        names = [t["name"] for t in resp.json().get("results", resp.json())]
        self.assertIn("Token A", names)
        self.assertNotIn("Other token", names)

    def test_delete_own_token(self):
        resp = self.client.post("/api/v1/accounts/me/tokens/", {"name": "Delete Me"})
        token_id = resp.json()["id"]
        del_resp = self.client.delete(f"/api/v1/accounts/me/tokens/{token_id}/")
        self.assertIn(del_resp.status_code, (200, 204))
        self.assertFalse(ApiKey.objects.filter(pk=token_id).exists())

    def test_cannot_delete_other_users_token(self):
        other = User.objects.create_user(
            email="other2@example.com", password="Pass123!", username="other2", tenant=self.tenant
        )
        raw = secrets.token_urlsafe(32)
        other_key = ApiKey.objects.create(
            tenant=self.tenant,
            user=other,
            name="Other token",
            key_prefix=raw[:8],
            key_hash=hashlib.sha256(raw.encode()).hexdigest(),
        )
        resp = self.client.delete(f"/api/v1/accounts/me/tokens/{other_key.pk}/")
        # Should be 404 (not in queryset) or 403
        self.assertIn(resp.status_code, (403, 404))

    def test_unauthenticated_access_denied(self):
        unauth_client = APIClient()
        resp = unauth_client.get("/api/v1/accounts/me/tokens/")
        self.assertIn(resp.status_code, (401, 403))

    def test_authenticate_api_with_personal_token(self):
        """End-to-end: create a PAT, then use it to authenticate a real API call."""
        resp = self.client.post("/api/v1/accounts/me/tokens/", {"name": "E2E Token"})
        token_value = resp.json()["token"]

        pat_client = APIClient()
        pat_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_value}")
        # The tokens endpoint itself requires auth — verify we can list tokens
        list_resp = pat_client.get("/api/v1/accounts/me/tokens/")
        self.assertEqual(list_resp.status_code, 200)
