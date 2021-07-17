from django.contrib import admin
from .models import (Product, Reviews, ProductImages, 
    Category, Wishlist)


class ProductAdmin(admin.ModelAdmin):
    search_fields = ['title',]
    list_filter = ['category',]
    list_editable = ['availability']
    list_display = ('title', 'category', 'availability', 'image_tag')
    prepopulated_fields = {'slug': ('title',)}

    def make_available(modeladmin, request, queryset):
        queryset.update(availability=True)
    
    def make_unavailable(modeladmin, request, queryset):
        queryset.update(availability=False)

    admin.site.add_action(make_available, "Mark as available")
    admin.site.add_action(make_unavailable, "Mark as unavailable")


class CategoryAdmin(admin.ModelAdmin):
    # list_display = ('')
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(ProductImages)
admin.site.register(Reviews)
admin.site.register(Wishlist)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)

