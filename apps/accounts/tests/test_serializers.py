from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.saas.models import Tenant
from apps.accounts.api.serializers import UserSerializer, ApiKeySerializer
from apps.accounts.models import Role, UserRole, UserProfile


class AccountsSerializerTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='T', slug='t')
        User = get_user_model()
        self.admin = User.objects.create_superuser(email='admin@example.com', password='pass123', username='admin', tenant=self.tenant)

    def test_user_serializer_creates_profile_when_profile_present(self):
        data = {
            'email': 'joe@example.com',
            'username': 'joe',
            'tenant': self.tenant.id,
            'password': 'pwd123',
            'profile': {'first_name': 'Joe', 'last_name': 'Tester'}
        }
        serializer = UserSerializer(data=data, context={'request': None})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        # profile should be created
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.first_name, 'Joe')
