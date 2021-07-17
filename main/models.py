from django.db import models
from django.conf import settings

# Create your models here.
class Newsletter(models.Model):
    email = models.EmailField(blank=False, null=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
