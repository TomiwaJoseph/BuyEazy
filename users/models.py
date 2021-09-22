from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from shop.models import Product, Order
from django.core.validators import RegexValidator


alphanumeric = RegexValidator(r'^^[a-zA-Z ]+$', 'Only letters and space are allowed.')

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, is_active=True, is_staff=False, is_admin=False, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email=email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, max_length=60)
    username = None
    user_order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    full_name = models.CharField(max_length=50, unique=False, validators=[alphanumeric])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects =  UserManager()

    def __str__(self):
        return self.full_name if self.full_name else self.email


class UserProfile(models.Model):
    user =  models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email


class Wishlist(models.Model):
    user =  models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
        related_name="wishlist_owner", null=True)
    folder = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return "{}'s wishlist".format(self.user)

