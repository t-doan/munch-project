from django.shortcuts import render
from .models import Address, Item, Customer, Payment, Food_Style

# Create your views here.
def home(request):
    addresses = Address.objects
    items = Item.objects
    customers = Customer.objects
    payments = Payment.objects
    food_styles = Food_Style.objects
    return render(request, 'tables/home.html',{
    'addresses': addresses,
    'items': items,
    'customers': customers,
    })
