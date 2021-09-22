from django.db import models
from django.conf import settings

# Create your models here.
class Newsletter(models.Model):
    email = models.EmailField(blank=False, null=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Gallery(models.Model):
    description = models.CharField(max_length=50)
    image = models.ImageField(upload_to="gallery")

    def __str__(self):
        return self.description

    class Meta:
        verbose_name_plural = "Gallery"