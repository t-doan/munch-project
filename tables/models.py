from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Address(models.Model):
    nickname = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=15)

    def __str__(self):
        return self.street + " " + self.city

class Restaurant(models.Model):
    #name
    name = models.CharField(max_length=50)
    #address
    address = models.CharField(max_length=50)
    #phone_number
    #max length on the table is 50 but i figure we should change this later
    phone_number = models.CharField(max_length=50)

    def __str__(self):
        return self.name + ' at ' + self.address

class Menu(models.Model):
    restaurant_id = models.ForeignKey(Restaurant,on_delete=models.CASCADE)

    def __str__(self):
        return 'Menu Id: ' + str(self.menu_id) + ' Rest. Id: '
        + str(self.restaurant_id)

class Item(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(decimal_places=2,max_digits=8)
    menu_id = models.ForeignKey(Menu,on_delete=models.CASCADE)
    is_spicy = models.BooleanField()

    def __str__(self):
        return self.name + " from menu: " + str(self.menu_id)

class Customer(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20, default='')
    stripeid = models.CharField(max_length=255)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

class Customer_Address(models.Model):
    address_id = models.ForeignKey(Address,on_delete=models.CASCADE)
    customer_id = models.ForeignKey(Customer,on_delete=models.CASCADE)

    def __str__(self):
        return 'Address: ' + str(self.address_id) + ' Customer: ' + str(self.customer_id)

class Payment (models.Model):
    #cardnumber
    card_number = models.BigIntegerField()
    #pin number
    card_pin = models.IntegerField()
    #Expiration Date
    card_expdate = models.DateField()

    def __str__(self):
        return 'Card Num: ' + str(self.card_number)

class Customer_Payment(models.Model):
    payment_id = models.ForeignKey(Payment,on_delete=models.CASCADE)
    customer_id = models.ForeignKey(Customer,on_delete=models.CASCADE)

    def __str__(self):
        return 'Payment Id: ' + str(self.payment_id) + ' Customer Id: ' + str(self.customer_id)

class Food_Style(models.Model):
    style_name = models.CharField(max_length=50)

    def __str__(self):
        return self.style_name

class Customer_Style_Preference(models.Model):
    style_id = models.ForeignKey(Food_Style,on_delete=models.CASCADE)
    customer_id = models.ForeignKey(Customer,on_delete=models.CASCADE)

    def __str__(self):
        return 'Style Id: ' + str(self.style_id) + ' Customer Id: ' + str(self.customer_id)

class Restaurant_Style(models.Model):
    #restaurant_id
    restaurant_id = models.ForeignKey(Restaurant,on_delete=models.CASCADE)
    #style_id
    style_id = models.ForeignKey(Food_Style,on_delete=models.CASCADE)

    def __str__(self):
        return 'Rest. Id: ' + str(self.restaurant_id) + ' Style Id:' + str(self.style_id)

class Review(models.Model):
    #text
    text = models.CharField(max_length=300)
    #stars
    stars = models.PositiveSmallIntegerField()
    #customer_id
    customer_id = models.ForeignKey(Customer,on_delete=models.CASCADE)
    #restaurant_id
    restaurant_id = models.ForeignKey(Restaurant,on_delete=models.CASCADE)

    def __str__(self):
        return 'Customer Id: ' + str(self.customer_id) + ' Rest. Id: '
        + str(self.restaurant_id) + ' ' + str(self.stars) + " stars"

class Item_Style(models.Model):
    item_id = models.ForeignKey(Item,on_delete=models.CASCADE)
    style_id = models.ForeignKey(Food_Style,on_delete=models.CASCADE)

    def __str__(self):
        return 'Item Id: ' + str(self.item_id) + ' Style. Id: '
        + str(self.style_id)
