from django.shortcuts import render
from .models import (Address, Item, Customer, Customer_Address,
Customer_Payment, Customer_Style_Preference, #Food_Style,
Item_Style, Menu, #Payment,
Restaurant, Restaurant_Style, Review)


# Create your views here.
def home(request):
    addresses = Address.objects
    items = Item.objects
    customers = Customer.objects
    customer_addresses = Customer_Address.objects
    customer_payments = Customer_Payment.objects
    customer_style_preferences = Customer_Style_Preference.objects
    #food_styles = Food_Style.objects

    item_styles = Item_Style.objects
    menus = Menu.objects
    #payments = Payment.objects

    restaurants = Restaurant.objects
    restaurant_styles = Restaurant_Style.objects
    reviews = Review.objects

    return render(request, 'tables/home.html',{
    'addresses': addresses,
    'items': items,
    'customers': customers,
    'customer_addresses': customer_addresses,
    'customer_payments': customer_payments,
    'customer_style_preferences': customer_style_preferences,
    # 'food_styles': food_styles,

    'item_styles': item_styles,
    'menus': menus,
    # 'payments': payments,

    'restaurants': restaurants,
    'restaurant_styles': restaurant_styles,
    'reviews': reviews
    })
