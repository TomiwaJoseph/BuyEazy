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

    path('create-payment-intent/', views.StripeIntentView.as_view(), name="create_payment_intent"),
    path('create-checkout-session/', views.CreateCheckoutSessionView.as_view(), name="create_checkout"),
    path('landing-view/', views.StripeLandingView.as_view(), name="stripe_landing"),
    path('success/', views.SuccessView.as_view(), name="success"),
    path('cancel/', views.CancelView.as_view(), name="cancel"),
    path('webhoks/stripe/', views.stripe_webhook, name="stripe_webhook"),
    
    
    path('test_page/', views.testpage, name='test'),
    path('save_review/', views.save_review, name='save_review'),
    path('shop/', views.shop, name='shop'),
    path('gallery/', views.gallery, name='gallery'),
    path('cart/', views.cart, name='cart'),
    path('request-refund/', views.RequestRefundView.as_view(), name='request_refund'),
    path('add-coupon/', views.AddCouponView.as_view(), name='add_coupon'),
    path('payment/<payment_option>/', views.PaymentView.as_view(), name='payment'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('view-product/<slug:slug>', views.SingleProduct.as_view(), name='view_product'),
]