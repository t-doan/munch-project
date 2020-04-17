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
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/', default='/static/NoImageFound.jpg')

    def __str__(self):
        return self.name + ' at ' + self.address

class Menu(models.Model):
    name = models.CharField(max_length=50)
    restaurant_id = models.ForeignKey(Restaurant,on_delete=models.CASCADE)

    def __str__(self):
        return 'Menu Name: ' + self.name + ' Menu Id: ' + str(self.id) + ' Rest. Id: '
        + str(self.restaurant_id)

class Item(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(decimal_places=2,max_digits=8)
    menu_id = models.ForeignKey(Menu,on_delete=models.CASCADE)
    is_spicy = models.BooleanField()
    image = models.ImageField(upload_to='images/', default='/static/NoImageFound.jpg')

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
    card_number = models.BigIntegerField()
    card_pin = models.IntegerField()
    card_expdate = models.DateField()

    def __str__(self):
        return 'Card Num: ' + str(self.card_number)

class Customer_Payment(models.Model):
    payment_id = models.ForeignKey(Payment,on_delete=models.CASCADE)
    customer_id = models.ForeignKey(Customer,on_delete=models.CASCADE)

    def __str__(self):
        return 'Payment Id: ' + str(self.payment_id) + ' Customer Id: ' + str(self.customer_id)

class Review(models.Model):
    text = models.CharField(max_length=300)
    stars = models.PositiveSmallIntegerField()
    customer_id = models.ForeignKey(Customer,on_delete=models.CASCADE)
    restaurant_id = models.ForeignKey(Restaurant,on_delete=models.CASCADE)

    def __str__(self):
        return 'Customer Id: ' + str(self.customer_id) + ' Rest. Id: '
        + str(self.restaurant_id) + ' ' + str(self.stars) + " stars"


class Cuisine(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Customer_Cuisine(models.Model):
    cuisine_id = models.ForeignKey(Cuisine,on_delete=models.CASCADE)
    customer_id = models.ForeignKey(Customer,on_delete=models.CASCADE)

    def __str__(self):
        return 'Cuisine Id: ' + str(self.cuisine_id) + ' Customer Id: ' + str(self.customer_id)

class Restaurant_Cuisine(models.Model):
    #restaurant_id
    restaurant_id = models.ForeignKey(Restaurant,on_delete=models.CASCADE)
    #style_id
    cuisine_id = models.ForeignKey(Cuisine,on_delete=models.CASCADE)

    def __str__(self):
        return 'Rest. Id: ' + str(self.restaurant_id) + ' Style Id:' + str(self.cuisine_id)

class Item_Cuisine(models.Model):
    item_id = models.ForeignKey(Item,on_delete=models.CASCADE)
    cuisine_id = models.ForeignKey(Cuisine,on_delete=models.CASCADE)

    def __str__(self):
        return 'Item Id: ' + str(self.item_id) + ' Cuisine. Id: '
        + str(self.cuisine_id)

# new branch stuff below
class CartItem(models.Model):
    item = models.OneToOneField(Item, on_delete=models.SET_NULL, null=True)
    is_ordered = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now=True)
    date_ordered = models.DateTimeField(null=True)
    # theres extra stuff here that im leaving for now

    def __str__(self):
        return self.product.name


class Cart(models.Model):
    ref_code = models.CharField(max_length=15)
    # owner = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    is_ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(CartItem)
    date_ordered = models.DateTimeField(auto_now=True)

    def get_cart_items(self):
        return self.items.all()

    def get_cart_total(self):
        return sum([item.item.price for item in self.items.all()])

    # def __str__(self):
    #     return '{0} - {1}'.format(self.owner, self.ref_code)
