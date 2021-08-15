from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, View, TemplateView
from .models import Product, Refund, ProductImages, Address, Order, OrderItem, Payment, Coupon, Reviews
from .forms import CheckoutForm, CouponForm, RefundForm
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
import string
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from users.models import Wishlist
import stripe
import json
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django_countries.data import COUNTRIES
# print(COUNTRIES.get('AU'))


stripe.api_key = settings.STRIPE_SECRET_KEY

# util functions

def create_ref_code():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=20))


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
                ordered_date = timezone.now()
                order = Order.objects.create(user=request.user,
                    ordered_date=ordered_date
                )
                order.product.add(item_to_cart)

        
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
            total_amount += int(item['quantity']) * int(item['price'])
        context = {
            'cart_data': request.session['cart_data'],
            'totalItems': len(request.session['cart_data']),
            'total_amount': total_amount,
        }
        print(total_amount)
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

    if request.user.is_authenticated:
        orderItem_to_delete = OrderItem.objects.get(user=request.user, product__id=request.GET['id'])
        order_qs = Order.objects.get(user=request.user, ordered=False)
        order_qs.product.remove(orderItem_to_delete)
        orderItem_to_delete.delete()

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

    if request.user.is_authenticated:
        product_id = int(request.GET['id'])
        orderItem_qs = OrderItem.objects.get(user=request.user, product__id=product_id, ordered=False)
        orderItem_qs.quantity = int(request.GET['qty'])
        orderItem_qs.save()

    t = render_to_string('shop/ajax_pages/cart_list.html', context)
    return JsonResponse({'data': t, 'totalItems': len(request.session['cart_data']), 'total_amount': total_amount})

def gallery(request):
    return render(request, 'shop/gallery.html')

def is_valid_form(values):
    valid = True
    for field in values:
        if field[0] == '':
            valid = False
    return valid


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order_qs = Order.objects.filter(user=self.request.user, ordered=False)
        if not order_qs.exists():
            order = Order.objects.create(user=self.request.user,
                ordered_date=timezone.now())
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
        # form = CheckoutForm()
        context = {
            'cart_contents': cart_contents,
            'form': CheckoutForm(),
            'couponform': CouponForm,
            'order': Order.objects.get(user=self.request.user, ordered=False),
        }
        shipping_address_qs = Address.objects.filter(
            user=self.request.user,
            address_type="S"
        )
        if shipping_address_qs.exists():
            context.update({'existing_shipping_address': shipping_address_qs[0]})
        billing_address_qs = Address.objects.filter(
            user=self.request.user,
            address_type="B"
        )
        if billing_address_qs.exists():
            context.update({'existing_billing_address': billing_address_qs[0]})
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
            
            know_if_same_shipping_as_billing = form.cleaned_data.get('same_shipping_address')
            know_if_to_overwrite_existing_shipping_address = form.cleaned_data.get('save_shipping_address')
            know_if_to_overwrite_existing_billing_address = form.cleaned_data.get('save_billing_address')
            know_if_to_use_default_billing = form.cleaned_data.get('use_default_billing')
            know_if_to_use_default_shipping = form.cleaned_data.get('use_default_shipping')
            payment_option = form.cleaned_data.get('payment_option')
            address_options = ['B', 'S']

            if know_if_to_use_default_shipping and know_if_to_use_default_billing:
                if payment_option == 'S':
                    return redirect('payment', 'stripe')
                elif payment_option == 'P':
                    return redirect('gallery')
            if know_if_to_use_default_shipping and not is_valid_form([billing_street_address,
                    billing_country, billing_zip_code]):
                messages.info(self.request, "Please fill in the required fields...")
                return redirect('checkout')
            if know_if_to_use_default_billing and not is_valid_form([shipping_street_address,
                    shipping_country, shipping_zip_code]):
                messages.info(self.request, "Please fill in the required fields...")
                return redirect('checkout')

            if not is_valid_form([shipping_street_address, shipping_country,
                shipping_zip_code, billing_street_address,
                billing_country, billing_zip_code]):
                messages.info(self.request, "Please fill in the required fields...")
                return redirect('checkout')
            
            if know_if_to_overwrite_existing_shipping_address:
                if is_valid_form([shipping_street_address,
                    shipping_country, shipping_zip_code]):
                    obj, created = Address.objects.update_or_create(
                        user = self.request.user, address_type="S",
                        defaults = {
                            'street_address': shipping_street_address[0],
                            'apartment_address': shipping_apartment_address[0],
                            'country': shipping_country[0],
                            'zip_code': shipping_zip_code[0],
                            'address_type': "S"
                        }
                    )
                    order.shipping_address = obj
                    order.save()
                else:
                    messages.info(self.request, "Please fill in the required fields...")
                    return redirect('checkout')
            if know_if_to_overwrite_existing_billing_address:
                if is_valid_form([billing_street_address,
                    billing_country, billing_zip_code]):
                    obj, created = Address.objects.update_or_create(
                        user = self.request.user, address_type="B",
                        defaults = {
                            'street_address': billing_street_address[0],
                            'apartment_address': billing_apartment_address[0],
                            'country': billing_country[0],
                            'zip_code': billing_zip_code[0],
                            'address_type': "B"
                        }
                    )
                    order.billing_address = obj
                    order.save()
                else:
                    messages.info(self.request, "Please fill in the required fields...")
                    return redirect('checkout')
            if know_if_same_shipping_as_billing:
                for option in address_options:
                    obj, created = Address.objects.update_or_create(
                        user = self.request.user, address_type=option,
                        defaults = {
                            'street_address': shipping_street_address[0],
                            'apartment_address': shipping_apartment_address[0],
                            'country': shipping_country[0],
                            'zip_code': shipping_zip_code[0],
                            'address_type': option
                        }
                    )
                    order.shipping_address = obj
                    order.billing_address = obj
                    order.save()
            
            if payment_option == 'S':
                return redirect('payment', 'stripe')
            elif payment_option == 'P':
                return redirect('gallery')


class PaymentView(View):
    def get(self, *args, **kwargs):
        try:
            cart_contents = OrderItem.objects.filter(
                user=self.request.user, ordered=False,
            )
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'cart_contents': cart_contents,
                # 'grand_total': order.get_total(),
                'order': order,
            }
            return render(self.request, "shop/payment.html", context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You have not added a billing address yet.")
            return redirect('checkout')

    def post(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            token = self.request.POST.get('stripeToken')
            amount = int(order.get_total() * 100)
            charge = stripe.Charge.create(
                amount = amount,
                currency = "usd",
                source = token,
            )

            # create the payment 
            payment = Payment()
            payment.stripe_charge_id = charge["id"]
            payment.user = self.request.user
            payment.amount = amount
            payment.save()

            # assign payment to the order
            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, "Your order was successful!")
            return redirect('gallery')

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect(".")
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect(".")
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.warning(self.request, "Invalid parameters")
            return redirect(".")
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not authenticated")
            return redirect(".")
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect(".")
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect(".")
        except Exception as e:
            # send an email to ourselves
            messages.warning(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect(".")


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


def testpage(request):
    if 'cart_data' in request.session:
        del request.session['cart_data']
    if request.user.is_authenticated:
        all_order_item = OrderItem.objects.filter(user=request.user, ordered=False)
        all_order_item.delete()
        order = Order.objects.filter(user=request.user, ordered=False)
        order.delete()
    messages.info(request, 'Something went wrong. You were not charged. Please try again.')
    return render(request, 'shop/test.html')

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

class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                try:
                    coupon = Coupon.objects.get(code=code)
                except ObjectDoesNotExist:
                    messages.info(self.request, "This coupon does not exist")
                    return redirect("checkout")
                order.coupon = coupon
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("checkout")


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


class SuccessView(TemplateView):
    template_name = "shop/success.html"


class CancelView(TemplateView):
    template_name = "shop/cancel.html"


class StripeLandingView(TemplateView):
    template_name = "shop/landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
        })
        return context


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = "http://127.0.0.8000"
        checkout_session = stripe.checkout.Session.create(
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
            payment_method_types=['card'],
            mode='payment',
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': 2000,
                        'product_data': {
                            'name': "single product",
                            # 'images': ['https://i.imgur.com/EHyR2nP.png']
                        },
                    },
                    'quantity': 7,
                },
            ],
        )
        return JsonResponse({
            "id": checkout_session.id
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

        # Save an order in your database, marked as 'awaiting payment'
        create_order(session)

        # Check if the order is already paid (e.g., from a card payment)
        #
        # A delayed notification payment will have an `unpaid` status, as
        # you're still waiting for funds to be transferred from the customer's
        # account.
        if session.payment_status == "paid":
            # Fulfill the purchase
            fulfill_order(session)

    elif event['type'] == 'checkout.session.async_payment_succeeded':
        session = event['data']['object']

        # Fulfill the purchase
        fulfill_order(session)

    elif event['type'] == 'checkout.session.async_payment_failed':
        session = event['data']['object']

        # Send an email to the customer asking them to retry their order
        email_customer_about_failed_payment(session)

    # Passed signature verification
    return HttpResponse(status=200)

def fulfill_order(session):
    # TODO: fill me in
    print("Fulfilling order")

def create_order(session):
    # TODO: fill me in
    print("Creating order")

def email_customer_about_failed_payment(session):
    # TODO: fill me in
    print("Emailing customer")




def calculate_order_amount():
    return 1270

class StripeIntentView(View):
    def post(self, request, *args, **kwargs):
        try:
            req_json = json.loads(request.body)
            customer = stripe.Customer.create(email=req_json['email'])
            intent = stripe.PaymentIntent.create(
                amount=calculate_order_amount(),
                currency='usd',
                customer=customer['id']
            )
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({ 'error': str(e) })

