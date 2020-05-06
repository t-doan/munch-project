from django.db import models
from django.contrib.auth.models import User
from decimal import *

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

class Address(models.Model):
    nickname = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=15)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

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
        return ('Menu: ' + str(self.id)+ ' ' + self.name + ' || Restaurant: ' + self.restaurant_id.name)

class Item(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(decimal_places=2,max_digits=8)
    menu_id = models.ForeignKey(Menu,on_delete=models.CASCADE)
    is_spicy = models.BooleanField()
    image = models.ImageField(upload_to='images/', default='/static/NoImageFound.jpg')

    def __str__(self):
        return self.name + " from menu: " + str(self.menu_id)

    def get_dict_of_model(self):
        return {
        'id': self.id,
        'name': self.name,
        'price': str(self.price),
        }

class Customer(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20, default='')
    stripeid = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

class Customer_Address(models.Model):
    address_id = models.ForeignKey(Address,on_delete=models.CASCADE)
    customer_id = models.ForeignKey(Customer,on_delete=models.CASCADE)

    def __str__(self):
        return 'Address: ' + str(self.address_id) + ' Customer: ' + str(self.customer_id)

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.customer) + " " + str(self.amount)

class Customer_Payment(models.Model):
    payment_id = models.ForeignKey(Payment,on_delete=models.CASCADE)
    customer_id = models.ForeignKey(Customer,on_delete=models.CASCADE)

    def __str__(self):
        return 'Payment Id: ' + str(self.payment_id) + ' Customer Id: ' + str(self.customer_id)

class Review(models.Model):
    header = models.CharField(max_length=50)
    text = models.CharField(max_length=500, blank=True, null=True)
    stars = models.PositiveSmallIntegerField()
    customer_id = models.ForeignKey(Customer,on_delete=models.CASCADE)
    restaurant_id = models.ForeignKey(Restaurant,on_delete=models.CASCADE)

    def __str__(self):
        return (str(self.stars) + ' stars' + ' Customer: '
        + str(self.customer_id) + ' Rest: ' + str(self.restaurant_id))

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
    restaurant_id = models.ForeignKey(Restaurant,on_delete=models.CASCADE)
    cuisine_id = models.ForeignKey(Cuisine,on_delete=models.CASCADE)

    def __str__(self):
        return 'Rest. Id: ' + str(self.restaurant_id) + ' Style Id:' + str(self.cuisine_id)

class Item_Cuisine(models.Model):
    item_id = models.ForeignKey(Item,on_delete=models.CASCADE)
    cuisine_id = models.ForeignKey(Cuisine,on_delete=models.CASCADE)

    def __str__(self):
        return 'Item Id: ' + str(self.item_id) + ' Cuisine. Id: ' + str(self.cuisine_id)

class OrderItem(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    note = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return str(self.customer) + ": " + str(self.quantity) + " " + self.item.name

    def get_total_item_price(self):
        return self.quantity * self.item.price


class Order(models.Model):
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    note = models.CharField(max_length=500, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    review = models.ForeignKey(Review,on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return str(self.customer) + " " + str(self.start_date)

    def get_subtotal(self):
        total = 0
        order_orderitems = list(Order_OrderItem.objects.filter(order=self))
        for order_orderitem in order_orderitems:
            order_item = order_orderitem.order_item
            total += order_item.get_total_item_price()
        return total

    def get_total_quantity(self):
        total = 0
        order_orderitems = list(Order_OrderItem.objects.filter(order=self))
        for order_orderitem in order_orderitems:
            order_item = order_orderitem.order_item
            total += order_item.quantity
        return total

    def get_order_list(self):
        order_list = dict()
        order_orderitems = list(Order_OrderItem.objects.filter(order=self))
        for order_orderitem in order_orderitems:
            orderitem = order_orderitem.order_item
            order_list[orderitem.item.name] = {
            'total_price': orderitem.get_total_item_price(),
            'quantity': orderitem.quantity,
            }
        return order_list

    # def get_restaurant(self):
    #     return str(list(Order_OrderItem.objects.filter(order=self))[0].order_item.item.menu_id.restaurant_id)

    def get_sales_tax(self):
        return Decimal(float(self.get_subtotal()) * 0.09).quantize(Decimal('0.01'))

class Order_OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)

    def __str__(self):
        return 'Order Cust: ' + str(self.order.customer) + ' OrderItem: ' + str(self.order_item)
