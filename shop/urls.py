from django.urls import path
from . import views

urlpatterns = [
    # Ajax Requests
    path('add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('load-more-products/', views.load_more_products, name='load_more_products'),
    path('delete-from-cart/', views.delete_cart_item, name='delete_cart_item'),
    path('update-cart/', views.update_cart_item, name='update_cart_item'),
    path('show-preview/', views.show_cart_preview, name='show_preview'),
    # Ajax Requests Ends

    path('test_page/', views.testpage, name='test'),
    path('shop/', views.shop, name='shop'),
    path('gallery/', views.gallery, name='gallery'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('view-product/<slug:slug>', views.SingleProduct.as_view(), name='view_product'),
]