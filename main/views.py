from django.shortcuts import render
from django.http import HttpResponse
from shop.models import Product, Category
import random
from .models import Newsletter, Gallery


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
    all_categories = []
    a = list(Product.objects.all())
    b = [i.title for i in list(Category.objects.all())]
    random.shuffle(b)
    random.shuffle(a)

    for num in range(4):
        l = [i for i in a if i.category.title == b[num]]
        all_categories.append(l[0])
    
    context = {
        'carousel': all_categories[:3],
        'all_categories': all_categories,
    }
    return render(request, 'main/index.html', context)

def contact(request):
    return render(request, 'main/contact.html')

def search_product(request):
    search_input = request.POST.get('search')
    query = Product.objects.filter(title__icontains=search_input)
    
    random_query = list(Product.objects.all())
    random.shuffle(random_query)
    all_categories = random_query[:4]
    
    context = {
        'search_input': search_input,
        'query': query,
        'interested': all_categories,
    }
    return render(request, 'main/search.html', context)

def gallery(request):
    all_gallery_pictures = list(Gallery.objects.all())
    random.shuffle(all_gallery_pictures)

    context = {
        'gallery_pictures': all_gallery_pictures[:13]
    }
    return render(request, 'main/gallery.html', context)


# TODO
# Social Auth
# Stripe, Paypal and Razor
# Dashboard address adn others