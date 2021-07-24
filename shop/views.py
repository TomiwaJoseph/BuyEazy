from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, View
from .models import Product, Wishlist
from .forms import CheckoutForm
# from users.models import CustomUser
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin


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
    cart_content = {}
    cart_content[str(request.GET['product_id'])] = {
        'title': request.GET['product_title'],
        'quantity': 1,
        'price': request.GET['product_price'],
        'image': request.GET['product_image'],
    }

    if 'cart_data' in request.session:
        if str(request.GET['product_id']) in request.session['cart_data']:
            all_items = request.session['cart_data']
            all_items[str(request.GET['product_id'])]['quantity'] = 1
            all_items.update(all_items)
            request.session['cart_data'] = all_items
        else:
            all_items = request.session['cart_data']
            all_items.update(cart_content)
            request.session['cart_data'] = all_items
    else:
        request.session['cart_data'] = cart_content
    return JsonResponse({'data': request.session['cart_data'], 'total_items': len(request.session['cart_data'])})

def show_cart_preview(request):
    try:
        session_cart = request.session['cart_data']
        all_cart_product_ids = [i for i in session_cart.keys()]
        cart_contents = [Product.objects.get(id=i) for i in all_cart_product_ids]
    except KeyError:
        cart_contents = []

    t = render_to_string('shop/ajax_pages/cart_content.html', {'cart_contents': cart_contents})
    return JsonResponse({'cart_contents': t})

def load_more_products(request):
    offset = int(request.GET.get('offset'))
    limit = int(request.GET.get('limit'))
    more_products = all_products[offset: offset + limit]

    t = render_to_string('shop/ajax_pages/more_products.html', {'more_products': more_products})
    return JsonResponse({'more_products': t, 'test': 2})

# Ajax Requests Ends

def shop(request):
    global all_products
    all_products = list(Product.objects.all())
    random.shuffle(all_products)

    context = {
        'all_products': all_products[:6],
        'total_products': Product.objects.count(),
    }
    return render(request, 'shop/shop.html', context)

def cart(request):
    total_amount = 0
    if 'cart_data' in request.session:
        for product_id, item in request.session['cart_data'].items():
            total_amount += int(item['quantity']) * float(item['price'])
        context = {
            'cart_data': request.session['cart_data'],
            'totalItems': len(request.session['cart_data']),
            'total_amount': int(round(total_amount, 1))
        }
        return render(request, 'shop/cart.html', context)
    else:
        return render(request, 'shop/cart.html', 
        {'cart_data': '', 'totalItems': 0, 'total_amt': total_amount})

def delete_cart_item(request):
    prod_id = str(request.GET['id'])
    if "cart_data" in request.session:
        if prod_id in request.session['cart_data']:
            cart_data = request.session['cart_data']
            del request.session['cart_data'][prod_id]
            request.session['cart_data'] = cart_data
    total_amount = 0
    for product_id, item in request.session['cart_data'].items():
        total_amount += int(item['quantity']) * float(item['price'])

    context = {
        'cart_data': request.session['cart_data'],
        'totalItems': len(request.session['cart_data']),
        'total_amount': int(round(total_amount, 1))
    }
    t = render_to_string('shop/ajax_pages/cart_list.html', context)
    return JsonResponse({'data': t, 'totalItems': len(request.session['cart_data']), 'total_amount': total_amount})

def update_cart_item(request):
    prod_id = str(request.GET['id'])
    prod_qty = request.GET['qty']
    if 'cart_data' in request.session:
        if prod_id in request.session['cart_data']:
            cart_data = request.session['cart_data']
            cart_data[prod_id]['quantity'] = prod_qty
            request.session['cart_data'] = cart_data
    total_amount = 0
    for product_id, item in request.session['cart_data'].items():
        total_amount += int(item['quantity']) * float(item['price'])
    
    context = {
        'cart_data': request.session['cart_data'],
        'totalItems': len(request.session['cart_data']),
        'total_amount': int(round(total_amount, 1))
    }
    t = render_to_string('shop/ajax_pages/cart_list.html', context)
    return JsonResponse({'data': t, 'totalItems': len(request.session['cart_data']), 'total_amount': total_amount})

def gallery(request):
    return render(request, 'shop/gallery.html')


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()

        if 'cart_data' in self.request.session:
            session_cart = self.request.session['cart_data']
            all_cart_product_ids = [i for i in session_cart.keys()]
            cart_contents = [Product.objects.get(id=i) for i in all_cart_product_ids]
        else: cart_contents = []

        context = {
            'cart_contents': cart_contents
        }
        return render(self.request, 'shop/checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        return redirect('contact')


class SingleProduct(DetailView):
    model = Product
    template_name = 'shop/single_product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def testpage(request):
    if 'cart_data' in request.session:
        del request.session['cart_data']
    return render(request, 'shop/test.html')