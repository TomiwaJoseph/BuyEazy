from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, View, TemplateView
from .models import Product, Refund, ProductImages, Address, Order, OrderItem, Reviews, Category
from .forms import CheckoutForm, RefundForm
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
import string
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from users.models import Wishlist, CustomUser
import stripe
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone


stripe.api_key = settings.STRIPE_SECRET_KEY

# util functions

def create_ref_code():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=20))

def is_valid_form(values):
    valid = True
    for field in values:
        if field[0] == '':
            valid = False
    return valid

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

    if request.user.is_authenticated:
        product_name = request.GET['product_title']
        orderItem_qs = OrderItem.objects.filter(user=request.user, ordered=False, 
            product__title=product_name)
        if not orderItem_qs:
            item_to_cart = OrderItem.objects.create(
                user=request.user,
                product = Product.objects.get(id=int(request.GET['product_id'])),
                quantity = 1,
                ordered = False
            )
            order_qs = Order.objects.filter(user=request.user, ordered=False)
            if order_qs.exists():
                order = order_qs.first()
                order.product.add(item_to_cart)
            else:
                order = Order.objects.create(user=request.user,
                    ref_code=create_ref_code()
                )
                order.product.add(item_to_cart)
                current_user = CustomUser.objects.get(email=request.user.email)
                current_user.user_order = order
                current_user.save()

    if request.user.is_authenticated:
        total_items = OrderItem.objects.filter(user=request.user, ordered=False).count()
    else:
        total_items = len(request.session['cart_data'])

        
    return JsonResponse({'data': request.session['cart_data'], 'total_items': total_items})

def show_cart_preview(request):
    try:
        if request.user.is_authenticated:
            all_user_order_item_ids = [i.product.id for i in OrderItem.objects.filter(user=request.user, ordered=False)]
            cart_contents = [Product.objects.get(id=i) for i in all_user_order_item_ids]
        else:
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
    return JsonResponse({'more_products': t})

def delete_cart_item(request):
    prod_id = str(request.GET['id'])
    context = {}
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

    if request.user.is_authenticated:
        orderItem_to_delete = OrderItem.objects.get(user=request.user, product__id=request.GET['id'], ordered=False)
        order_qs = Order.objects.get(user=request.user, ordered=False)
        order_qs.product.remove(orderItem_to_delete)
        orderItem_to_delete.delete()

        cart_dict = {}
        orderItem_qs = OrderItem.objects.filter(user=request.user, ordered=False)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if orderItem_qs.exists():
            for obj in orderItem_qs:
                cart_dict.update({f"{obj.product.id}": {'title': obj.product.title, 'quantity': obj.quantity, 
                    'price': f'{obj.product.discount_price}', 'image': f'{obj.product.main_image.url}'}})
            context.update({"cart_data": cart_dict})
        if order_qs.exists():
            context.update({"totalItems": order_qs[0].get_unordered_cart_items_count})
            context.update({"total_amount": order_qs[0].get_total})

        total_items = OrderItem.objects.filter(user=request.user, ordered=False).count()
        context.update({"totalItems": total_items})
    
        total_items = OrderItem.objects.filter(user=request.user, ordered=False).count()
        totalAmount = order_qs[0].get_total()
    else:
        total_items = len(request.session['cart_data'])
        totalAmount = total_amount

    t = render_to_string('shop/ajax_pages/cart_list.html', context)
    return JsonResponse({'data': t, 'totalItems': total_items, 'total_amount': totalAmount})

def update_cart_item(request):
    prod_id = str(request.GET['id'])
    prod_qty = request.GET['qty']
    context = {}
    if 'cart_data' in request.session:
        if prod_id in request.session['cart_data']:
            cart_data = request.session['cart_data']
            cart_data[prod_id]['quantity'] = prod_qty
            request.session['cart_data'] = cart_data
        total_amount = 0
        for product_id, item in request.session['cart_data'].items():
            total_amount += int(item['quantity']) * float(item['price'])
    
        context.update({
            'cart_data': request.session['cart_data'],
            'totalItems': len(request.session['cart_data']),
            'total_amount': int(round(total_amount, 1))
        })

    if request.user.is_authenticated:
        cart_dict = {}
        product_id = int(request.GET['id'])
        orderItem_qs = OrderItem.objects.get(user=request.user, product__id=product_id, ordered=False)
        orderItem_qs.quantity = int(request.GET['qty'])
        orderItem_qs.save()

        orderItem_qs = OrderItem.objects.filter(user=request.user, ordered=False)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if orderItem_qs.exists():
            for obj in orderItem_qs:
                cart_dict.update({f"{obj.product.id}": {'title': obj.product.title, 'quantity': obj.quantity, 
                    'price': f'{obj.product.discount_price}', 'image': f'{obj.product.main_image.url}'}})
            context.update({"cart_data": cart_dict})
        if order_qs.exists():
            context.update({"totalItems": order_qs[0].get_unordered_cart_items_count})
            context.update({"total_amount": order_qs[0].get_total})

        total_items = OrderItem.objects.filter(user=request.user, ordered=False).count()
        context.update({"totalItems": total_items})
    
        total_items = OrderItem.objects.filter(user=request.user, ordered=False).count()
        totalAmount = order_qs[0].get_total()
    else:
        total_items = len(request.session['cart_data'])
        totalAmount = total_amount

    t = render_to_string('shop/ajax_pages/cart_list.html', context)
    return JsonResponse({'data': t, 'totalItems': total_items, 'total_amount': totalAmount})

def filter_category(request):
    category_to_filter = request.GET.get('_category')
    filtered_products = Product.objects.filter(category__title=category_to_filter)
    t = render_to_string('shop/ajax_pages/filter_products.html', {'filtered_products': filtered_products})
    return JsonResponse({'filtered_products': t, 'category': category_to_filter})

def filter_price_and_product(request):
    selected = request.POST.getlist('category')
    min_value = int(request.POST.get('min-value')[1:])
    max_value = int(request.POST.get('max-value')[1:])
    filtered_products = Product.objects.filter(
        category__title__in=selected,
        discount_price__gte=min_value, discount_price__lte=max_value
    )
    t = render_to_string('shop/ajax_pages/filter_price_product.html', {'filtered_products': filtered_products})
    return JsonResponse({'filtered_products': t})

# Ajax Requests Ends

def shop(request):
    global all_products
    all_products = list(Product.objects.all())
    random.shuffle(all_products)
    context = {
        'all_categories': Category.objects.all(),
        'all_products': all_products[:6],
        'total_products': Product.objects.count(),
        'cart_size': 0
    }
    if request.user.is_authenticated:
        qs = Order.objects.filter(user=request.user, ordered=False)
        if qs.exists():
            context.update({"cart_size": qs[0].get_unordered_cart_items_count})
    return render(request, 'shop/shop.html', context)

def cart(request):
    cart_dict = {}
    context = {}
    if request.user.is_authenticated:
        orderItem_qs = OrderItem.objects.filter(user=request.user, ordered=False)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if orderItem_qs.exists():
            for obj in orderItem_qs:
                cart_dict.update({f"{obj.product.id}": {'title': obj.product.title, 'quantity': obj.quantity, 
                    'price': f'{obj.product.discount_price}', 'image': f'{obj.product.main_image.url}'}})
            context.update({"cart_data": cart_dict})
        if order_qs.exists():
            context.update({"totalItems": order_qs[0].get_unordered_cart_items_count})
            context.update({"total_amount": order_qs[0].get_total})

        return render(request, 'shop/cart.html', context)
    else:
        total_amount = 0
        if 'cart_data' in request.session:
            for product_id, item in request.session['cart_data'].items():
                total_amount += int(item['quantity']) * int(item['price'])
            context = {
                'cart_data': request.session['cart_data'],
                'totalItems': len(request.session['cart_data']),
                'total_amount': total_amount,
            }
            return render(request, 'shop/cart.html', context)
        else:
            return render(request, 'shop/cart.html', 
            {'cart_data': '', 'totalItems': 0, 'total_amt': total_amount})


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order_qs = Order.objects.filter(user=self.request.user, ordered=False)
        if not order_qs.exists():
            order = Order.objects.create(user=self.request.user,
                ref_code=create_ref_code())
            for product_id, item_data in self.request.session['cart_data'].items():
                item_to_order = OrderItem.objects.create(
                    user = self.request.user,
                    product = Product.objects.get(id=int(product_id)),
                    quantity = item_data['quantity'],
                    ordered = False,
                )
                order.product.add(item_to_order)

        cart_contents = OrderItem.objects.filter(
            user=self.request.user, ordered=False,
        )
        context = {
            'cart_contents': cart_contents,
            'form': CheckoutForm(),
        }
        default_shipping_address_qs = Address.objects.filter(
            user=self.request.user,
            address_type="S",
            default=True
        )
        if default_shipping_address_qs.exists():
            context.update({'default_shipping_address': default_shipping_address_qs[0]})

        default_billing_address_qs = Address.objects.filter(
            user=self.request.user,
            address_type="B",
            default=True
        )
        if default_billing_address_qs.exists():
            context.update({'default_billing_address': default_billing_address_qs[0]})
        return render(self.request, 'shop/checkout.html', context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = CheckoutForm(self.request.POST or None)
        if form.is_valid():
            shipping_street_address = form.cleaned_data.get('shipping_address'),
            shipping_apartment_address = form.cleaned_data.get('shipping_address2'),
            shipping_country = form.cleaned_data.get('shipping_country'),
            shipping_zip_code = form.cleaned_data.get('shipping_zip'),

            billing_street_address = form.cleaned_data.get('billing_address'),
            billing_apartment_address = form.cleaned_data.get('billing_address2'),
            billing_country = form.cleaned_data.get('billing_country'),
            billing_zip_code = form.cleaned_data.get('billing_zip'),
            
            know_if_to_save_shipping_address_as_default = form.cleaned_data.get('save_shipping_address')
            know_if_to_save_billing_address_as_default = form.cleaned_data.get('save_billing_address')
            know_if_to_use_default_shipping = form.cleaned_data.get('use_default_shipping')
            know_if_to_use_default_billing = form.cleaned_data.get('use_default_billing')
            user_order = Order.objects.get(user=self.request.user, ordered=False)
            address_options = ['B', 'S']

            if know_if_to_use_default_shipping and know_if_to_use_default_billing:
                user_billing_address = Address.objects.get(user=self.request.user, default=True, address_type='B')
                user_shipping_address = Address.objects.get(user=self.request.user, default=True, address_type='S')
                user_order.billing_address = user_billing_address
                user_order.shipping_address = user_shipping_address
                user_order.save()

            elif is_valid_form([shipping_street_address, shipping_country,
                    shipping_zip_code, billing_street_address,
                    billing_country, billing_zip_code]):
                new_billing_address = Address.objects.create(
                    user = self.request.user,
                    street_address = billing_street_address[0],
                    apartment_address = billing_apartment_address[0],
                    country = billing_country[0],
                    zip_code = billing_zip_code[0],
                    address_type = "B",
                    default = False
                )
                new_shipping_address = Address.objects.create(
                    user = self.request.user,
                    street_address = shipping_street_address[0],
                    apartment_address = shipping_apartment_address[0],
                    country = shipping_country[0],
                    zip_code = shipping_zip_code[0],
                    address_type = "S",
                    default = False
                )
                user_order.billing_address = new_billing_address
                user_order.shipping_address = new_shipping_address
                user_order.save()
                if know_if_to_save_shipping_address_as_default:
                    user_default_shipping = Address.objects.filter(user=self.request.user, address_type='S',
                        default=True).update(default=False)
                    new_shipping_address.default = True
                    new_shipping_address.save()
                if know_if_to_save_billing_address_as_default:
                    all_user_billing = Address.objects.filter(user=self.request.user, address_type='B',
                        default=True).update(default=False)
                    new_billing_address.default = True
                    new_billing_address.save()

            elif know_if_to_use_default_shipping and is_valid_form([billing_street_address,
                billing_country, billing_zip_code]):
                user_shipping_address = Address.objects.get(user=self.request.user, default=True, address_type='S')
                new_billing_address = Address.objects.create(
                    user = self.request.user,
                    street_address = billing_street_address[0],
                    apartment_address = billing_apartment_address[0],
                    country = billing_country[0],
                    zip_code = billing_zip_code[0],
                    address_type = "B",
                    default = False
                )
                user_order.billing_address = new_billing_address
                user_order.shipping_address = user_shipping_address
                user_order.save()
                if know_if_to_save_billing_address_as_default:
                    all_user_billing = Address.objects.filter(user=self.request.user, address_type='B',
                        default=True).update(default=False)
                    new_billing_address.default = True
                    new_billing_address.save()

            elif know_if_to_use_default_billing and is_valid_form([shipping_street_address,
                shipping_country, shipping_zip_code]):
                user_billing_address = Address.objects.get(user=self.request.user, default=True, address_type='B')
                new_shipping_address = Address.objects.create(
                    user = self.request.user,
                    street_address = shipping_street_address[0],
                    apartment_address = shipping_apartment_address[0],
                    country = shipping_country[0],
                    zip_code = shipping_zip_code[0],
                    address_type = "S",
                    default = False
                )
                user_order.billing_address = user_billing_address
                user_order.shipping_address = new_shipping_address
                user_order.save()
                if know_if_to_save_shipping_address_as_default:
                    user_default_shipping = Address.objects.filter(user=self.request.user, address_type='S',
                        default=True).update(default=False)
                    new_shipping_address.default = True
                    new_shipping_address.save()

            else:
                messages.error(self.request, "Please fill in the required fields...")
                return redirect('checkout')

            return redirect('payment_page')


@login_required
def payment_page(request):    
    cart_contents = OrderItem.objects.filter(
        user=request.user, ordered=False,
    )
    order = Order.objects.get(user=request.user, ordered=False)
    context = {
        'cart_contents': cart_contents,
        'order': order,
        "STRIPE_PUBLISHABLE_KEY": settings.STRIPE_PUBLISHABLE_KEY
    }
    return render(request, "shop/payment_page.html", context)


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        order_items = OrderItem.objects.filter(
            user=request.user, ordered=False,
        )
        order = Order.objects.get(
            user=request.user, ordered=False,
        )
        domain_url = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items = [{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': item.get_stripe_price(),
                    'product_data': {
                        'name': item.product.title,
                        # 'images': [item.product.main_image.path],
                    },
                },
                'quantity': item.quantity,
            } for item in order_items],
            metadata={
                "products": order.id,
                "current_user_email": self.request.user.email,
            },
            mode='payment',
            success_url = domain_url + '/shop/purchase/stripe/success/',
            cancel_url = domain_url + '/shop/purchase/stripe/cancel/',
        )
        return JsonResponse({
            'id': checkout_session.id
        })


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
                
        customer_email = session["customer_details"]["email"]
        order_id = session["metadata"]["products"]
        email = session["metadata"]["current_user_email"]
                
        order = Order.objects.get(id=int(order_id))
        order_products = order.product.all()
        
        if order_products.count() > 1:
            the_string = "Thanks for buying: \n\n"
            for i, q in enumerate(order_products, 1):
                the_string += str(i) + '. ' + str(q.product.title) + '\n'
            message = the_string + '\nEnjoy!'
        else:
            item = order_products.first().product.title
            message=f'Thanks for buying "{item}".\nEnjoy!'
            
        send_mail(
            subject="Product Purchase",
            message=message,
            recipient_list=[customer_email],
            from_email=settings.EMAIL_HOST_USER
        )
        
        order.ordered = True
        order.paid_for = True
        order.payment_date = timezone.now()
        order.being_processed = True
        order.save()
        
        for order_item in order_products:
            order_item.ordered = True
            order_item.save()
            
    return HttpResponse(status=200)


class SuccessView(TemplateView):
    template_name = "shop/success.html"


class CancelView(TemplateView):
    template_name = "shop/cancel.html"


class PaypalPaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order_details = Order.objects.filter(user=self.request.user, ordered=False)
        context = {
            "order_details": order_details[0],
        }
        return render(self.request, "shop/paypal_payment.html", context)

    def post(self, *args, **kwargs):
        pass


class SingleProduct(DetailView):
    model = Product
    template_name = 'shop/single_product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = context.get('object')
        get_product = Product.objects.get(id=qs.id)
        context['similar_products'] = Product.objects.filter(category=qs.category).exclude(id=qs.id)[:4]
        context['related_products'] = Product.objects.all()
        context['all_other_images'] = ProductImages.objects.filter(product_id=context['object'])
        context['all_reviews'] = Reviews.objects.filter(product_id=context['object'])
        return context


@login_required
def save_review(request):
    to_redirect_to = request.POST.get('to_redirect')
    message = request.POST.get('message')
    review = Reviews.objects.create(
        product_id = Product.objects.get(slug=to_redirect_to),
        review = message,
        reviewer = request.user
    )
    return redirect("view_product", to_redirect_to)


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "shop/request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("request_refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "You don't have an order with the reference code provided.")
                return redirect("request_refund")


"""

    stripe listen --forward-to localhost:8000/webhooks/stripe
    4242424242424242 Works
    4000000000009995 Insufficient funds
    4000002500003155 authentication not handled

"""