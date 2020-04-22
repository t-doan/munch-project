from django.contrib import admin
from .models import (Address, Item, Customer, Customer_Address,
Customer_Payment, Customer_Cuisine, Cuisine, Order, OrderItem, Order_OrderItem,
Item_Cuisine, Menu, Payment, Restaurant, Restaurant_Cuisine, Review)

admin.site.register(Address)
admin.site.register(Item)
admin.site.register(Customer)
admin.site.register(Customer_Address)
admin.site.register(Customer_Payment)
admin.site.register(Customer_Cuisine)
admin.site.register(Cuisine)
admin.site.register(Item_Cuisine)
admin.site.register(Menu)
admin.site.register(Payment)
admin.site.register(Restaurant)
admin.site.register(Restaurant_Cuisine)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Order_OrderItem)
