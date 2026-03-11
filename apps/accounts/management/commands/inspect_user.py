from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Inspect a user account by email'

    def add_arguments(self, parser):
        parser.add_argument('email')

    def handle(self, *args, **options):
        email = options['email']
        User = get_user_model()
        u = User.objects.filter(email=email).first()
        if not u:
            self.stdout.write(self.style.ERROR('User not found'))
            return
        self.stdout.write(f'User: {u.email}, username={u.username}, tenant={getattr(u, "tenant", None)}, is_staff={u.is_staff}, is_superuser={u.is_superuser}, is_active={u.is_active}')
        try:
            ok = u.check_password('TestPass123')
            self.stdout.write(f'Password matches TestPass123: {ok}')
        except Exception as e:
            self.stdout.write(f'Password check error: {e}')
        try:
            urs = u.user_roles.all()
            self.stdout.write(f'UserRoles count: {urs.count()}')
            for ur in urs:
                self.stdout.write(f'  role: {ur.role.code} / {ur.role.name}')
        except Exception as e:
            self.stdout.write(f'UserRole error: {e}')
