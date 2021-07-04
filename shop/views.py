from django.shortcuts import render
from django.views.generic import DetailView

# Create your views here.
def shop(request):
    return render(request, 'shop/shop.html')

def single_product(request):
    return render(request, 'shop/single_product.html')


# class SingleProduct(DetailView):
#     model = Something
#     template_name = 'shop/single_product.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context