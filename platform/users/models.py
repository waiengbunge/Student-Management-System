from django.contrib.auth.models import AbstractUser

from django.db import models

from platform.core.models import Organization


class User(AbstractUser):
    ROLE_CHOICES = [
        ('system_admin', 'System Admin'),
        ('school_admin', 'School Admin'),
        ('teacher', 'Teacher'),
        ('accountant', 'Accountant'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='users')
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username