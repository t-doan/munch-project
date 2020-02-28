from django.db import models

# Create your models here.
class Address(models.Model):
    street = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.IntegerField()

    def __str__(self):
        return self.street + " " + self.city

class Item(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(decimal_places=2,max_digits=8)
    menu_id = models.IntegerField()
    is_spicy = models.BooleanField()

    def __str__(self):
        return self.name + " from menu: " + str(self.menu_id)

class Customer(models.Model):
    #first_name
    first_name = models.CharField(max_length=50)
    #last_name
    last_name = models.CharField(max_length=50)
    #phone_number
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

class Payment (models.Model):
    ##Name on CharField
    cardholder_FirstName = models.CharField(max_length=50)
    cardholder_LastName = models.CharField(max_length=50)
    #card number
    card_number = models.CharField(max_length=50)
    #CVV card number
    CVV_number = models.IntegerField()
    #zipcode
    card_zip = models.IntegerField()
    #Card Expiration Data
    card_expdate = models.IntegerField()

    def __str__(self):
        return self.cardholder_FirstName + " " + self.cardholder_LastName + " " + self.card_number + " " + self.CVV_number + " " + self.card_expdate

class Food_Style (models.Model):
    food_style = models.CharField(max_length=50)

    def __str__(self):
        return self.food_style
