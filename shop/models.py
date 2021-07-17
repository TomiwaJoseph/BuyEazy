from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    category = models.ForeignKey("Category", on_delete=models.CASCADE,
        related_name="product_category")
    operating_system = models.CharField(max_length=50)
    processor = models.CharField(max_length=150)
    processor_technology = models.CharField(max_length=100)
    graphics = models.CharField(max_length=100)
    memory = models.CharField(max_length=100)
    hard_drive = models.CharField(max_length=100)
    wireless = models.CharField(max_length=100)
    power_supply = models.CharField(max_length=100)
    battery = models.CharField(max_length=100)
    main_image = models.ImageField(upload_to="products")
    price = models.CharField(max_length=10)
    slug = models.SlugField(max_length=100)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('view_product', args=[self.slug])

    def image_tag(self):
        return mark_safe("<img src='{}' height='20'/>".format(self.main_image.url))

    image_tag.short_description = "Image"


class Reviews(models.Model):
    product_id = models.ForeignKey("Product", 
        on_delete=models.CASCADE, related_name="reviewed_product")
    review = models.CharField(max_length=100, blank=False)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_reviewed =  models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} reviewed {}'.format(self.reviewer, self.product_id)

    class Meta:
        verbose_name_plural = 'Reviews'
        ordering = ('-date_reviewed',)


class Category(models.Model):
    title = models.CharField(max_length=50, blank=False)
    description = models.CharField(max_length=100, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=50)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'Categories'


class ProductImages(models.Model):
    product_id = models.ForeignKey("Product", on_delete=models.CASCADE,
        related_name="product_images")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="products/sub_images")

    def __str__(self):
        return "images of {}".format(self.product_id.title)
    
    class Meta:
        verbose_name = 'Product Images'
        verbose_name_plural = 'Product Images'


class Wishlist(models.Model):
    user =  models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
        related_name="wishlist_owner")
    folder = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return "{}'s wishlist".format(self.user)

