from django.contrib import admin
from .models import (Product, Reviews, ProductImages, Refund,
    Category, OrderItem, Order, Payment, Coupon, Address)


class ProductAdmin(admin.ModelAdmin):
    search_fields = ['title',]
    list_filter = ['category',]
    list_editable = ['category', 'price', 'discount_price']
    list_display = ('title', 'price', 'discount_price', 'category', 'image_tag')
    prepopulated_fields = {'slug': ('title',)}


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity']


class OrderAdmin(admin.ModelAdmin):
    list_editable = ['being_delivered', 'received', 'refund_requested', 'refund_granted']
    list_display = ['user', 'ordered', 'being_delivered', 'received',
        'refund_requested', 'refund_granted', 'coupon']


class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_address', 'country', 'address_type']


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(ProductImages)
admin.site.register(Address, AddressAdmin)
admin.site.register(Coupon)
admin.site.register(Payment)
admin.site.register(Reviews)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)

