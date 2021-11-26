from django.contrib import admin
from .models import (Product, Reviews, ProductImages, Refund,
    Category, OrderItem, Order, Coupon, Address)


class ProductAdmin(admin.ModelAdmin):
    search_fields = ['title',]
    list_filter = ['category',]
    list_editable = ['category', 'discount_price', 'real_price']
    list_display = ('title', 'discount_price', 'real_price', 'category', 'image_tag')
    prepopulated_fields = {'slug': ('title',)}


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered', 'product', 'quantity']
    list_editable = ['ordered']


class OrderAdmin(admin.ModelAdmin):
    list_editable = ['being_processed', 'delivered', 'refund_requested', 'refund_granted']
    list_display = ['user', 'ref_code', 'ordered', 'paid_for', 'payment_date', 'being_processed', 'delivered',
        'refund_requested', 'refund_granted', 'coupon']


class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'default', 'street_address', 'country', 'address_type']
    list_editable = ['default']


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(ProductImages)
admin.site.register(Address, AddressAdmin)
admin.site.register(Coupon)
admin.site.register(Reviews)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)

