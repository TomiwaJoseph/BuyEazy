from .base import *
from decouple import config


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['tomiwajoseph-ecommerce.herokuapp.com']

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
