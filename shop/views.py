from django.shortcuts import render
from django.views.generic import DetailView
from .models import Product, Wishlist
# from users.models import CustomUser
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Ajax Requests Start

def add_to_wishlist(request):
    product_id =  int(request.GET.get('product_id'))
    product_to_add_to_wishlist = Product.objects.get(id=product_id)
    check_wishlist_exist = Wishlist.objects.filter(user=request.user).first()
    if check_wishlist_exist:
        check_product_exist = product_id in [i.id for i in check_wishlist_exist.folder.all()]
        if not check_product_exist:
            check_wishlist_exist.folder.add(product_to_add_to_wishlist)
    else: 
        create_new = Wishlist.objects.create(user=request.user)
        create_new
        create_new.folder.add(product_to_add_to_wishlist)
    return HttpResponse("Success!")

def add_to_cart(request):
    product_id =  int(request.GET.get('product_id'))
    product_to_add_to_cart = Product.objects.get(id=product_id)

    return HttpResponse("Success!")

# Ajax Requests Ends

def shop(request):
    return render(request, 'shop/shop.html')

# def single_product(request):
#     return render(request, 'shop/single_product.html')

def checkout_view(request):
    return render(request, 'shop/checkout.html')


class SingleProduct(DetailView):
    model = Product
    template_name = 'shop/single_product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def all_categories(request):
    every_category = Product.objects.all()

    every_cat = request.GET.get('page', 1)
    every_cat_paginator = Paginator(every_category, 5)

    every_desk = request.GET.get('page', 1)
    every_desk_paginator = Paginator(every_category, 5)

    every_tab = request.GET.get('page', 1)
    every_tab_paginator = Paginator(every_category, 5)

    every_hybri = request.GET.get('page', 1)
    every_hybri_paginator = Paginator(every_category, 5)

    try:
        all_category = every_cat_paginator.page(every_cat)
    except PageNotAnInteger:
        all_category = every_cat_paginator.page(1)
    except EmptyPage:
        all_category = every_cat_paginator.page(every_cat.num_pages)

    context = {
        'all_category': all_category,
    }
    return render(request, 'shop/detail.html')


def testpage(request):
    return render(request, 'shop/test.html')