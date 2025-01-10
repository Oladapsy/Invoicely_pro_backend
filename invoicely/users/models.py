from django.db import models
# want to inherit from the Django Abstraction... to inherit from it and use its authentication
from django.contrib.auth.models import AbstractUser


# Create your models here.
class CustomUser(AbstractUser):
    username = None  # Remove the default username field
    full_name = models.CharField(max_length=150)
    company_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True)  # Use email as the unique identifier
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    USERNAME_FIELD = 'email'  # Email is the unique identifier
    REQUIRED_FIELDS = ['full_name']  # Fields required for superuser creation

    def __str__(self):
        return f'{self.email} - {self.full_name}'


