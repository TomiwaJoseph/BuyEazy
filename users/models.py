from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')

# class CustomUser(AbstractUser):
#     email = models.EmailField(unique=True, max_length=60)
#     username = models.CharField(max_length=50, unique=True, validators=[alphanumeric])

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []

#     def __str__(self):
#         return self.username


