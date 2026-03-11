"""Management command: generate a personal access token for a user.

Usage:
    python -m config.manage create_pat user@example.com --name "VS Code Agent" --days 90

The raw token is printed to stdout once. Store it securely — it is not
recoverable from the database (only its SHA-256 hash is stored).
"""

import hashlib
import secrets
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    help = "Generate a personal access token for the given user"

    def add_arguments(self, parser):
        parser.add_argument("email", help="Email of the user to create the token for")
        parser.add_argument(
            "--name",
            default="CLI Token",
            help='Descriptive name for the token (default: "CLI Token")',
        )
        parser.add_argument(
            "--days",
            type=int,
            default=None,
            help="Number of days until the token expires (omit for no expiry)",
        )

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model
        from apps.accounts.models import ApiKey

        User = get_user_model()
        email = options["email"]

        user = User.objects.filter(email=email).first()
        if not user:
            raise CommandError(f"No user found with email: {email}")

        if not user.is_active:
            raise CommandError(f"User {email} is inactive.")

        tenant = getattr(user, "tenant", None)
        if tenant is None:
            raise CommandError(f"User {email} has no tenant assigned.")

        name = options["name"]
        expires_at = None
        if options["days"] is not None:
            if options["days"] < 1:
                raise CommandError("--days must be a positive integer.")
            expires_at = timezone.now() + timedelta(days=options["days"])

        token = secrets.token_urlsafe(32)
        prefix = token[:8]
        key_hash = hashlib.sha256(token.encode()).hexdigest()

        api_key = ApiKey.objects.create(
            tenant=tenant,
            user=user,
            name=name,
            key_prefix=prefix,
            key_hash=key_hash,
            expires_at=expires_at,
        )

        self.stdout.write(self.style.SUCCESS(f"\nPersonal access token created for {email}"))
        self.stdout.write(f"  Name   : {api_key.name}")
        self.stdout.write(f"  Prefix : {api_key.key_prefix}...")
        if expires_at:
            self.stdout.write(f"  Expires: {expires_at.strftime('%Y-%m-%d')}")
        else:
            self.stdout.write("  Expires: never")
        self.stdout.write(self.style.WARNING(f"\n  Token  : {token}\n"))
        self.stdout.write(
            "  Use it in the Authorization header:\n"
            f"    Authorization: ****** {token}\n"
        )
        self.stdout.write(
            self.style.WARNING(
                "  WARNING: This token will not be shown again. Store it securely.\n"
            )
        )
