"""Tests for the personal access token UI views at /accounts/tokens/."""

import hashlib
import secrets

from django.test import TestCase, Client
from django.urls import reverse

from apps.accounts.models import ApiKey, User
from apps.saas.models import Campus, Tenant


class PersonalTokenViewTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="ViewTenant", slug="viewtenant")
        self.campus = Campus.objects.create(tenant=self.tenant, name="Main", code="VTMAIN")
        self.user = User.objects.create_user(
            email="view_user@example.com",
            password="TestPass123",
            username="view_user",
            tenant=self.tenant,
        )
        self.client = Client()
        self.client.force_login(self.user)

    # ── listing ──────────────────────────────────────────────────────────────

    def test_list_page_requires_login(self):
        self.client.logout()
        resp = self.client.get(reverse("personal_tokens"))
        self.assertRedirects(resp, f"/login/?next={reverse('personal_tokens')}", fetch_redirect_response=False)

    def test_list_page_renders(self):
        resp = self.client.get(reverse("personal_tokens"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Personal Access Tokens")

    def test_list_page_shows_existing_tokens(self):
        raw = secrets.token_urlsafe(32)
        ApiKey.objects.create(
            tenant=self.tenant,
            user=self.user,
            name="My Token",
            key_prefix=raw[:8],
            key_hash=hashlib.sha256(raw.encode()).hexdigest(),
        )
        resp = self.client.get(reverse("personal_tokens"))
        self.assertContains(resp, "My Token")

    def test_list_page_does_not_show_other_users_tokens(self):
        other = User.objects.create_user(
            email="other@example.com", password="TestPass123", username="other", tenant=self.tenant
        )
        raw = secrets.token_urlsafe(32)
        ApiKey.objects.create(
            tenant=self.tenant,
            user=other,
            name="Other Token",
            key_prefix=raw[:8],
            key_hash=hashlib.sha256(raw.encode()).hexdigest(),
        )
        resp = self.client.get(reverse("personal_tokens"))
        self.assertNotContains(resp, "Other Token")

    # ── creation ─────────────────────────────────────────────────────────────

    def test_create_token_requires_login(self):
        self.client.logout()
        resp = self.client.post(reverse("personal_tokens_create"), {"name": "X"})
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login/", resp["Location"])

    def test_create_token_success(self):
        resp = self.client.post(
            reverse("personal_tokens_create"), {"name": "VS Code Agent"}
        )
        self.assertRedirects(resp, reverse("personal_tokens"), fetch_redirect_response=False)
        self.assertTrue(ApiKey.objects.filter(user=self.user, name="VS Code Agent").exists())

    def test_create_token_stores_plain_token_in_session_once(self):
        self.client.post(reverse("personal_tokens_create"), {"name": "Session Token"})
        # follow the redirect — should show the raw token
        resp = self.client.get(reverse("personal_tokens"))
        self.assertContains(resp, "Session Token")
        # token is removed from session after one display
        resp2 = self.client.get(reverse("personal_tokens"))
        # the second GET should not have the "copy it now" alert for this token
        self.assertNotContains(resp2, "copy it now", msg_prefix="Token should only be shown once")

    def test_create_token_sets_correct_owner_and_tenant(self):
        self.client.post(reverse("personal_tokens_create"), {"name": "Owner Check"})
        key = ApiKey.objects.get(user=self.user, name="Owner Check")
        self.assertEqual(key.user, self.user)
        self.assertEqual(key.tenant, self.tenant)

    def test_create_token_with_expiry(self):
        self.client.post(
            reverse("personal_tokens_create"), {"name": "Expiring", "expires_days": "30"}
        )
        key = ApiKey.objects.get(user=self.user, name="Expiring")
        self.assertIsNotNone(key.expires_at)

    def test_create_token_bad_expiry_rejected(self):
        resp = self.client.post(
            reverse("personal_tokens_create"), {"name": "Bad Expiry", "expires_days": "abc"}
        )
        self.assertRedirects(resp, reverse("personal_tokens"), fetch_redirect_response=False)
        self.assertFalse(ApiKey.objects.filter(user=self.user, name="Bad Expiry").exists())

    def test_create_token_missing_name_rejected(self):
        resp = self.client.post(reverse("personal_tokens_create"), {"name": ""})
        self.assertRedirects(resp, reverse("personal_tokens"), fetch_redirect_response=False)

    # ── deletion ─────────────────────────────────────────────────────────────

    def test_delete_own_token(self):
        raw = secrets.token_urlsafe(32)
        key = ApiKey.objects.create(
            tenant=self.tenant,
            user=self.user,
            name="Doomed",
            key_prefix=raw[:8],
            key_hash=hashlib.sha256(raw.encode()).hexdigest(),
        )
        resp = self.client.post(reverse("personal_tokens_delete", args=[key.pk]))
        self.assertRedirects(resp, reverse("personal_tokens"), fetch_redirect_response=False)
        self.assertFalse(ApiKey.objects.filter(pk=key.pk).exists())

    def test_cannot_delete_other_users_token(self):
        other = User.objects.create_user(
            email="other2@example.com", password="TestPass123", username="other2", tenant=self.tenant
        )
        raw = secrets.token_urlsafe(32)
        other_key = ApiKey.objects.create(
            tenant=self.tenant,
            user=other,
            name="Other Doomed",
            key_prefix=raw[:8],
            key_hash=hashlib.sha256(raw.encode()).hexdigest(),
        )
        resp = self.client.post(reverse("personal_tokens_delete", args=[other_key.pk]))
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(ApiKey.objects.filter(pk=other_key.pk).exists())

    def test_delete_requires_login(self):
        self.client.logout()
        raw = secrets.token_urlsafe(32)
        key = ApiKey.objects.create(
            tenant=self.tenant,
            user=self.user,
            name="Protected",
            key_prefix=raw[:8],
            key_hash=hashlib.sha256(raw.encode()).hexdigest(),
        )
        resp = self.client.post(reverse("personal_tokens_delete", args=[key.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login/", resp["Location"])
        self.assertTrue(ApiKey.objects.filter(pk=key.pk).exists())
