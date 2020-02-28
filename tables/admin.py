from django.contrib import admin
from .models import Address, Item, Customer, Payment, Food_Style

# Register your models here.
admin.site.register(Address)
admin.site.register(Item)
admin.site.register(Customer)
admin.site.register(Payment)
admin.site.register(Food_Style)
