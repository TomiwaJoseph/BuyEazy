from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from .models import UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_profile, sender=settings.AUTH_USER_MODEL)
