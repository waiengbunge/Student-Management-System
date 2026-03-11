import hashlib
import secrets
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    help = 'Generate a Personal Access Token (PAT) for a user.'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address of the user')
        parser.add_argument('--name', type=str, default='CLI Token', help='Descriptive name for the token')
        parser.add_argument('--days', type=int, default=None, help='Number of days until the token expires (omit for no expiry)')

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model
        from apps.accounts.models import ApiKey

        User = get_user_model()
        email = options['email']
        name = options['name']
        days = options['days']

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise CommandError(f'No user found with email: {email}')

        token = secrets.token_urlsafe(32)
        prefix = token[:8]
        key_hash = hashlib.sha256(token.encode()).hexdigest()
        expires_at = None
        if days:
            expires_at = timezone.now() + datetime.timedelta(days=days)

        ApiKey.objects.create(
            tenant=user.tenant,
            user=user,
            name=name,
            key_prefix=prefix,
            key_hash=key_hash,
            expires_at=expires_at,
            is_active=True,
        )

        self.stdout.write(self.style.SUCCESS(f'Token  : {token}'))
        self.stdout.write(f'Use:   Authorization: Bearer {token}')
        if expires_at:
            self.stdout.write(f'Expires: {expires_at.strftime("%Y-%m-%d")}')
        else:
            self.stdout.write('Expires: Never')
