from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from .models import UserProfile
from django.contrib.auth.signals import user_logged_in
from shop.models import Order, OrderItem, Product
from shop.views import create_ref_code


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_profile, sender=settings.AUTH_USER_MODEL)


@receiver(user_logged_in)
def on_login(sender, user, request, **kwargs):
    try:
        cart_data = request.session['cart_data']
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if not order_qs.exists():
            order = Order.objects.create(
                user=request.user,
                ref_code=create_ref_code(),
            )
            order.save()
        
        order = Order.objects.get(user=request.user, ordered=False)
        for product_id, item_data in cart_data.items():
            orderItem_qs = OrderItem.objects.filter(user=request.user, ordered=False, 
                product__id=product_id)
            if not orderItem_qs.exists():
                item_to_order = OrderItem.objects.create(
                    user = request.user,
                    product = Product.objects.get(id=int(product_id)),
                    quantity = item_data['quantity'],
                    ordered = False,
                )
                order.product.add(item_to_order)
    except KeyError:
        pass
