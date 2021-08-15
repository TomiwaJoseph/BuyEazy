from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from .forms import (LoginForm, RegisterForm)
from shop.models import OrderItem, Order
from .models import Wishlist
from django.contrib.auth.decorators import login_required

# Create your views here.

class MyLoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'


def register(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def logout_view(request):
    # all_orders = Order.objects.filter(user=request.user, ordered=False)
    # all_orders.delete()
    # all_order_items = OrderItem.objects.filter(user=request.user, ordered=False)
    # all_order_items.delete()
    logout(request)
    return redirect('index')

@login_required
def dashboard(request):
    all_wishlist = Wishlist.objects.filter(user=request.user)
    context = {
        'all_wishlist': all_wishlist,
    }
    return render(request, 'users/dashboard.html', context)
