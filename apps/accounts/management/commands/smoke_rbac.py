from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Smoke test RBAC by logging in seeded users and requesting dashboard'

    def handle(self, *args, **options):
        User = get_user_model()
        clients = {}
        users = User.objects.filter(email__in=[
            'system_admin@example.com','managing_director@example.com','training_manager@example.com',
            'registrar@example.com','instructor@example.com','accountant@example.com','cashier@example.com',
            'receptionist@example.com','marketing_manager@example.com','student@example.com'
        ])
        if not users.exists():
            self.stdout.write(self.style.ERROR('No seeded users found. Run seed_rbac first.'))
            return

        for u in users:
            c = Client()
            login_data = {'username': u.email, 'password': 'TestPass123'}
            resp = c.post(reverse('login'), login_data, follow=True)
            ok = resp.status_code == 200
            location = resp.redirect_chain[-1][0] if resp.redirect_chain else resp.request.get('PATH_INFO')
            self.stdout.write(f'{u.email} -> status={resp.status_code}, final_path={location}, ok={ok}')
            # try dashboard
            d = c.get(reverse('dashboard'))
            self.stdout.write(f'  dashboard: {d.status_code}')

        self.stdout.write(self.style.SUCCESS('Smoke RBAC completed'))
