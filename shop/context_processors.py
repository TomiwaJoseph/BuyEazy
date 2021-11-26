from django.conf import settings

def get_categories(request):
    return {
        'email': settings.EMAIL_HOST_USER,
    }