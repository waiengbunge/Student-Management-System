from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Ensure seeded users have known password TestPass123'

    def handle(self, *args, **options):
        emails = ['system_admin@example.com','managing_director@example.com','training_manager@example.com',
            'registrar@example.com','instructor@example.com','accountant@example.com','cashier@example.com',
            'receptionist@example.com','marketing_manager@example.com','student@example.com']
        User = get_user_model()
        for email in emails:
            u = User.objects.filter(email=email).first()
            if not u:
                self.stdout.write(self.style.WARNING(f'User not found: {email}'))
                continue
            u.set_password('TestPass123')
            u.save()
            self.stdout.write(self.style.SUCCESS(f'Password set for {email}'))
        self.stdout.write(self.style.SUCCESS('Passwords ensured.'))
