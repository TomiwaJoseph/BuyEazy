from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from decouple import config

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates a superuser.'

    def handle(self, *args, **options):
        if not User.objects.filter(email=config('EMAIL_HOST_USER')).exists():
            User.objects.create_superuser(
                email=config("EMAIL_HOST_USER"),
                password=config("ADMIN_PASSWORD")
            )
