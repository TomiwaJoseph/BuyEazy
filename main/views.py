from django.shortcuts import render
from django.http import HttpResponse
from shop.models import Product, Category
import random
from .models import Newsletter


# Ajax Requests Start

def newsletter(request):
    get_email = request.POST.get('email')
    email_in_newsletter = Newsletter.objects.filter(email=get_email)
    if not email_in_newsletter:
        new_email = Newsletter.objects.create(email=get_email)
        new_email

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

# def newsletter(request):
#     get_email = request.POST.get('email')
#     # if get_email:
#     #     new_email = Newsletter.objects.create(email=get_email)
#     #     new_email.save()
#     return HttpResponse(status=204)

