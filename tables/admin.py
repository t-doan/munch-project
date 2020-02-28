from django.contrib import admin
from .models import (Address, Item, Customer, Customer_Address,
 Customer_Payment, Customer_Style_Preference, #Food_Style,
 Item_Style, Menu, #Payment,
 Restaurant, Restaurant_Style, Review)

# Register your models here.
admin.site.register(Address)
admin.site.register(Item)
admin.site.register(Customer)
admin.site.register(Customer_Address)
admin.site.register(Customer_Payment)
admin.site.register(Customer_Style_Preference)
#admin.site.register(Food_Style)
admin.site.register(Item_Style)
admin.site.register(Menu)
# admin.site.register(Payment)
admin.site.register(Restaurant)
admin.site.register(Restaurant_Style)
admin.site.register(Review)
