from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_countries.fields import CountryField


ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)


class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    category = models.ForeignKey("Category", on_delete=models.CASCADE,
                                 related_name="product_category", null=True)
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
    real_price = models.PositiveIntegerField()
    discount_price = models.PositiveIntegerField()
    slug = models.SlugField(max_length=100)
    other_product_images = models.ManyToManyField("ProductImages")

    def __str__(self):
        return self.title

    def get_stripe_price(self):
        return int(self.discount_price) * 100

    def get_absolute_url(self):
        return reverse('view_product', args=[self.slug])

    def image_tag(self):
        return mark_safe("<img src='{}' height='30'/>".format(self.main_image.url))

    image_tag.short_description = "Image"


class Reviews(models.Model):
    product_id = models.ForeignKey("Product", null=True,
                                   on_delete=models.CASCADE, related_name="reviewed_product")
    review = models.CharField(max_length=100, blank=False)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    date_reviewed = models.DateTimeField(auto_now_add=True)

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
                                   related_name="product_images", null=True)
    # title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="products/sub_images")

    def __str__(self):
        return "image of {}".format(self.product_id)

    class Meta:
        verbose_name = 'Product Images'
        verbose_name_plural = 'Product Images'


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} of {self.product.title}"

    def get_total_item_price(self):
        return self.quantity * self.product.discount_price

    def get_stripe_price(self):
        return self.product.discount_price * 100


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    product = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey('Address', related_name="shipping_address",
                                         on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey('Address', related_name="billing_address",
                                        on_delete=models.SET_NULL, blank=True, null=True)
    paid_for = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    being_processed = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        # return self.user.email
        return "{}'s order".format(self.user)

    def get_unordered_cart_items_count(self):
        if self.ordered == False:
            return self.product.all().count()
        return 0

    def get_total(self):
        total = 0
        for order_item in self.product.all():
            total += order_item.get_total_item_price()
        return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip_code = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        if self.address_type == 'B':
            return "{}'s billing address".format(self.user)
        return "{}'s shipping address".format(self.user)

    class Meta:
        verbose_name_plural = 'Addresses'


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"
