from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from .forms import (LoginForm, RegisterForm, UserUpdateForm, ChangePasswordForm)
from shop.models import OrderItem, Order, Address, Product
from .models import Wishlist, CustomUser
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate
from django.db.models import Count
from django.db.models.functions import ExtractMonth
import calendar
from random import shuffle

from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage


# Ajax Requests

def delete_wishlist_item(request):
    product_to_delete = request.GET.get('id')
    wishlist_object_qs = Wishlist.objects.get(user=request.user)
    wishlist_object_qs.folder.remove(Product.objects.get(id=product_to_delete))
    wishlist_products = Wishlist.objects.filter(user=request.user)
    t = render_to_string('users/ajax_pages/wishlist_list.html', {'wishlist_products': wishlist_products})
    return JsonResponse({'wishlist_products': t,})

def show_order_details(request):
    order_to_show = request.GET.get('ref_code')
    order_details_qs = Order.objects.filter(user=request.user, ref_code=order_to_show)
    if order_details_qs.exists():
        order_details = order_details_qs[0]
    t = render_to_string('users/ajax_pages/show_order_details.html', {'order_details': order_details})
    return JsonResponse({'order_details': t,})

# Ajax Requests ends

class MyLoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_products = list(Product.objects.all())
        shuffle(all_products)
        context['random_product'] = all_products[0]
        return context


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request).domain
            link = reverse('activate', kwargs={
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user)
            })
            activate_url = current_site + link

            mail_subject = 'Activate your EazyBuy account'
            message = 'Hi! Please click this link to complete your registration\n' + activate_url
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to = [to_email])
            email.send(fail_silently=True)
            return redirect('awaiting_activation')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def awaiting_activation(request):
    return render(request, "registration/awaiting_activation.html")

@login_required
def dashboard(request):
    paid_orders = Order.objects.filter(paid_for=True, user=request.user).annotate(month=ExtractMonth('payment_date')).values('month').annotate(count=Count('id')).values('month','count')
    monthNumber = []
    totalOrders = []
    for d in paid_orders:
        monthNumber.append(calendar.month_name[d['month']])
        totalOrders.append(d['count'])

    change_password_form = ChangePasswordForm()
    update_form = UserUpdateForm(instance=request.user)
    context = {
        'monthNumber': monthNumber, 'totalOrders': totalOrders,
        'change_password_form': change_password_form,
        'update_form': update_form,
        'all_wishlist': Wishlist.objects.filter(user=request.user),
        'user_address_qs': Address.objects.filter(user=request.user, default=True),
        'completed_orders': Order.objects.filter(user=request.user, paid_for=True)
    }

    if request.method == "POST":
        update_form = UserUpdateForm(request.POST, instance=request.user)
        change_password_form = ChangePasswordForm(request.POST)
        
        if update_form.is_valid():
            update_form.save()
            messages.info(request, "Full name has been successfully updated!")
            return redirect('dashboard')

        if change_password_form.is_valid():
            email = request.user.email
            password = change_password_form.cleaned_data['old_password']
            new_password = change_password_form.cleaned_data['new_password1']

            user = authenticate(username=email, password=password)
            if user is not None:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password was been successfully updated!")
                return redirect('dashboard')
            else:
                messages.error(request, "You entered a wrong old password or your new password don't match")
                return render(request, 'users/dashboard.html', context)
            
    return render(request, 'users/dashboard.html', context)

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Welcome! Enjoy the buy.")
        return redirect('index')
    else:
        return HttpResponse('Activation link is invalid')
    