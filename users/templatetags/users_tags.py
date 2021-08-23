from django import template
from django_countries.data import COUNTRIES


register = template.Library()

@register.filter
def lookup_country(country):
    return COUNTRIES.get(country)

@register.filter
def lookup_address_type(addr):
    return 'Billing address' if addr == 'B' else 'Shipping address'
        
