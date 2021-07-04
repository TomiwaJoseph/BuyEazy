from django.urls import path
from . import views

urlpatterns = [
    path('shop/', views.shop, name='shop'),
    path('single_product/', views.single_product, name='single_product'),
]