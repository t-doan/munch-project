from django.shortcuts import render
from .models import Address, Item, Customer
# Create your views here.
def home(request):
    addresses = Address.objects
    items = Item.objects
    customers = Customer.objects
    return render(request, 'tables/home.html',{
    'addresses': addresses,
    'items': items,
    'customers': customers,
    })
