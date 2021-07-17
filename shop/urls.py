from django.urls import path
from . import views

urlpatterns = [
    # Ajax Requests
    path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    # Ajax Requests Ends

    path('test_page/', views.testpage, name='test'),
    path('shop/', views.shop, name='shop'),
    path('checkout/', views.checkout_view, name='checkout'),
    # path('view_product/<slug:slug>', views.single_product, name='view_product'),
    path('view_product/<slug:slug>', views.SingleProduct.as_view(), name='view_product'),
]