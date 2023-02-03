from django.shortcuts import render, redirect
from django.http import HttpResponse
from shop.models import Product, Category
from .models import Newsletter, Gallery
from random import shuffle, SystemRandom
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings


# Ajax Requests Start

def newsletter(request):
    get_email = request.POST.get('email')
    email_in_newsletter = Newsletter.objects.filter(email=get_email)
    if not email_in_newsletter:
        new_email = Newsletter.objects.create(email=get_email)
        new_email.save()

    return HttpResponse('Success')

# Ajax Requests Ends


def index(request):
    sys_random = SystemRandom()
    all_products = list(Product.objects.all())
    carousel_images = sys_random.choices(all_products, k=3)

    all_categories = []
    found_categories = []
    while len(all_categories) != 4:
        sys_random.shuffle(all_products)
        for product in all_products:
            if product.category.title not in found_categories:
                all_categories.append(product)
                found_categories.append(product.category.title)

    context = {
        'carousel': carousel_images,
        'all_categories': all_categories,
    }
    return render(request, 'main/index.html', context)


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        email = request.POST.get('email')
        message = request.POST.get('message')

        intro_and_message = f"Hi, {name} here.\n" + message

        try:
            send_mail(subject, intro_and_message, email,
                      [settings.EMAIL_HOST_USER], fail_silently=False)
            messages.success(request, 'Message sent successfully')
        except Exception as e:
            messages.error(request, 'Message not sent. Try again.')

    return render(request, 'main/contact.html')


def search_product(request):
    search_input = request.POST.get('search')
    query = Product.objects.filter(title__icontains=search_input)

    random_query = list(Product.objects.all())
    shuffle(random_query)
    all_categories = random_query[:4]

    context = {
        'search_input': search_input,
        'query': query,
        'interested': all_categories,
    }
    return render(request, 'main/search.html', context)


def gallery(request):
    all_gallery_pictures = list(Gallery.objects.all())
    shuffle(all_gallery_pictures)

    context = {
        'gallery_pictures': all_gallery_pictures[:13]
    }
    return render(request, 'main/gallery.html', context)
