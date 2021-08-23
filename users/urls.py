from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Ajax Requests
    path('delete-wishlist-item/', views.delete_wishlist_item, name='delete_wishlist_item'),
    path('show-order-details/', views.show_order_details, name='show_order_details'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name="registration/password_reset.html"), 
        name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name="registration/password_reset_done.html"), 
        name='password_reset_done'),
    path('password-reset-confim/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="registration/password_reset_confirm.html"), 
        name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name="registration/password_reset_complete.html"), 
        name='password_reset_complete'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.MyLoginView.as_view(
        redirect_authenticated_user=True), name='login'),
    # path('login/', auth_views.LoginView.as_view(
    #     redirect_authenticated_user=True), name='login'),
    path('register/', views.register, name='register'),
    path('awaiting-activation/', views.awaiting_activation, name='awaiting_activation'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]