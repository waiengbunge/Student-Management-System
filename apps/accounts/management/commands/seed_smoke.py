from django.core.management.base import BaseCommand
from django.core import management


class Command(BaseCommand):
    help = 'Run minimal seed and smoke checks (seeds demo data and runs basic smoke tasks)'

    def handle(self, *args, **options):
        # run existing seed demo if available
        try:
            management.call_command('seed_demo')
        except Exception:
            self.stdout.write(self.style.WARNING('seed_demo command not available or failed'))

        # run smoke RBAC if available
        try:
            management.call_command('smoke_rbac')
        except Exception:
            self.stdout.write(self.style.WARNING('smoke_rbac command not available or failed'))

        self.stdout.write(self.style.SUCCESS('Smoke seed complete'))
