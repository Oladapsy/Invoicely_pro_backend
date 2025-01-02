from django.db import models
# want to inherit from the Django Abstraction... to inherit from it and use its authentication
from django.contrib.auth.models import AbstractUser


# Create your models here.
class CustomUser(AbstractUser):
    name = models.CharField(max_length=100)