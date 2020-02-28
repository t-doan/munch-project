from django.contrib import admin
from .models import Address, Item, Customer

# Register your models here.
admin.site.register(Address)
admin.site.register(Item)
admin.site.register(Customer)
