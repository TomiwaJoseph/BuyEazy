from django.urls import path
from . import views

urlpatterns = [
    # Ajax Requests
    path('specific-category/', views.filter_category, name='filter_category'),
    path('specific-category-and-price/', views.filter_price_and_product, name='filter_price_and_product'),
    path('add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('load-more-products/', views.load_more_products, name='load_more_products'),
    path('delete-from-cart/', views.delete_cart_item, name='delete_cart_item'),
    path('update-cart/', views.update_cart_item, name='update_cart_item'),
    path('show-preview/', views.show_cart_preview, name='show_preview'),
    path('shop/checkout/payment/', views.payment_page, name='payment_page'),
    # Ajax Requests Ends

    # Stripe
    path('shop/purchase/stripe/success/', views.SuccessView.as_view(), name="success"),
    path('shop/purchase/stripe/cancel/', views.CancelView.as_view(), name="cancel"),
    path('create-checkout-session/', views.CreateCheckoutSessionView.as_view(), name='create_payment'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe-webhook'),

    #To use for project
    # path('create-payment-intent/', views.StripeIntentView.as_view(), name="create_payment_intent"),
    # path('webhooks/stripe/', views.stripe_webhook, name="stripe_webhook"),
    # path('payment/stripe/', views.StripeLandingView.as_view(), name="stripe_payment"),
    # path('payment/paypal/', views.PaypalPaymentView.as_view(), name='paypal_payment'),
    # End Stripe    
    
    path('save_review/', views.save_review, name='save_review'),
    path('shop/', views.shop, name='shop'),
    path('cart/', views.cart, name='cart'),
    path('request-refund/', views.RequestRefundView.as_view(), name='request_refund'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('view-product/<slug:slug>', views.SingleProduct.as_view(), name='view_product'),
]