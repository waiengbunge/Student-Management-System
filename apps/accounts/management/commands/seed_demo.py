from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from apps.saas.models import Tenant


class Command(BaseCommand):
    help = 'Seed demo tenant, groups and users (admin, instructor, student)'

    def handle(self, *args, **options):
        User = get_user_model()

        tenant, _ = Tenant.objects.get_or_create(slug='demo', defaults={'name': 'Demo Tenant'})

        groups = ['Student', 'Instructor', 'Training Manager', 'Registrar', 'Accounts', 'Parent']
        for g in groups:
            Group.objects.get_or_create(name=g)

        # superuser
        if not User.objects.filter(email='admin@example.com').exists():
            User.objects.create_superuser(email='admin@example.com', username='admin', password='AdminPass123', tenant=tenant)
            self.stdout.write(self.style.SUCCESS('Created superuser admin@example.com / AdminPass123'))

        # instructor
        if not User.objects.filter(email='instructor1@example.com').exists():
            u = User.objects.create_user(email='instructor1@example.com', username='instructor1', password='password123', tenant=tenant)
            grp = Group.objects.get(name='Instructor')
            grp.user_set.add(u)
            u.is_staff = True
            u.save()
            self.stdout.write(self.style.SUCCESS('Created instructor instructor1 / password123'))

        # student
        if not User.objects.filter(email='student1@example.com').exists():
            s = User.objects.create_user(email='student1@example.com', username='student1', password='password123', tenant=tenant)
            grp = Group.objects.get(name='Student')
            grp.user_set.add(s)
            s.save()
            self.stdout.write(self.style.SUCCESS('Created student student1 / password123'))

        self.stdout.write(self.style.SUCCESS('Demo seed complete'))
