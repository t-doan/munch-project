from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .forms import CustomSignupForm, CustomerForm, AddressForm, OrderInfoForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
import stripe
import googlemaps
import json
from decouple import config

from .models import Restaurant, Menu, Item, Cuisine, Customer_Cuisine, Order, OrderItem, Order_OrderItem
from .models import Address, Customer, Customer_Address, Restaurant_Cuisine

stripe.api_key = config('STRIPE_API_KEY')
gmaps = googlemaps.Client(key=config('GOOGLE_API_KEY'))

def home(request):
    return render (request, 'tables/home.html')

def load_dashboard(request):
    address_str = request.POST.get('search_address')
    print(address_str)
    restaurants = Restaurant.objects.all()
    restaurant_dists = {}
    for restaurant in restaurants:
        my_dist = gmaps.distance_matrix(address_str, restaurant.address, units='imperial')['rows'][0]['elements'][0]
        print(my_dist)
        restaurant_dists[restaurant.name + ' text'] = my_dist['distance']['text'] + 'les'
        restaurant_dists[restaurant.name + ' value'] = my_dist['distance']['value']
    print(restaurant_dists)
    context = {
    'restaurants':restaurants,
    'restaurant_dists':restaurant_dists,
    }
    return render(request, 'tables/dashboard.html', context = context)

def restaurantView(request, restaurant_id):
    restaurant = Restaurant.objects.get(pk = restaurant_id)
    menu_objs = list(Menu.objects.filter(restaurant_id_id=restaurant.id))
    menu_items = []
    menu_names = []
    for menu in menu_objs:
        menu_names.append(menu.name)
        items = list(Item.objects.filter(menu_id=menu.id))
        menu_items.append(items)
    rest_cuisines = list(Restaurant_Cuisine.objects.filter(restaurant_id_id=restaurant.id))
    if len(rest_cuisines) == 0:
        cuisines_str = ""
    else:
        cuisines_str = "Cuisines:"
        for rest_cuis in rest_cuisines:
            cuisines_str = cuisines_str + " " + Cuisine.objects.get(id = rest_cuis.cuisine_id_id).name + ","
        cuisines_str = cuisines_str[:len(cuisines_str)-1]
    chosen_items = { "name" : "John" }

    context = {
    'restaurant':restaurant,
    'menu_names':menu_names,
    'menu_items':menu_items,
    'i_amt':range(len(menu_names)),
    'cuisines_str':cuisines_str,
    'chosen_items': json.dumps(chosen_items),
    }
    return render(request, 'tables/restaurant_view.html',context = context)

def profile(request):
    customer = Customer.objects.get(user_id = request.user.id)
    customer_addresses = list(Customer_Address.objects.filter(customer_id_id=customer.id))
    addresses = []
    for cust_add in customer_addresses:
        addresses.append(Address.objects.get(id = cust_add.address_id_id))
    cust_cuisines = list(Customer_Cuisine.objects.filter(customer_id_id=customer.id))
    cuisines = []
    for cust_cuis in cust_cuisines:
        cuisines.append(Cuisine.objects.get(id = cust_cuis.cuisine_id_id))
    return render(request, 'account/user-profile.html', {'customer':customer, 'addresses':addresses, 'cuisines':cuisines})

class SignUp(generic.CreateView):
    form_class = CustomSignupForm
    success_url = reverse_lazy('fillCustomer')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        valid = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return valid

def fillCustomer(request):
     if request.method == 'POST':
        filled_form = CustomerForm(request.POST)
        if filled_form.is_valid():
            created_customer = filled_form.save(commit=False)
            created_customer.user = request.user
            created_customer.save()
            created_customer_pk = created_customer.id
            address_form = AddressForm()
            return render(request, 'registration/address.html', {'form':address_form, 'created_customer_pk':created_customer_pk})
        else:
            note = 'Form not valid. Please try again'
            customer_form = CustomerForm()
            return render(request, 'registration/customer-registration.html', {'form':customer_form, 'note':note})
     else:
        customer_form = CustomerForm()
        return render(request, 'registration/customer-registration.html', {'form':customer_form})

def edit_customer(request):
    customer = Customer.objects.get(user_id=request.user.id)
    form = CustomerForm(instance = customer)
    if request.method == 'POST':
        filled_form = CustomerForm(request.POST, instance=customer)
        if filled_form.is_valid():
            filled_form.save()
            form = filled_form
            note = 'Your info has been successfully changed'
        else:
            note = 'There was an error in changing your information'
        return render(request, 'account/edit_customer.html', {'form':form, 'note':note})
    return render(request, 'account/edit_customer.html', {'form':form})

def fillAddress(request):
        filled_form = AddressForm(request.POST)

        if filled_form.is_valid():
            created_address = filled_form.save()
            created_address_pk = created_address.id
            filled_form = AddressForm()
            address = Address.objects.get(id = created_address_pk)
            customer = Customer.objects.get(user_id=request.user.id)
            customer_address = Customer_Address(address_id=address, customer_id=customer)
            customer_address.save()
        else:
            created_address_pk = None
        return render(request, 'tables/home.html', {'created_address_pk':created_address_pk})


def add_address(request, customer_id):
    if request.method == 'POST':
        filled_form = AddressForm(request.POST)

        if filled_form.is_valid():
            created_address = filled_form.save()
            created_address_pk = created_address.id
            filled_form = AddressForm()
            address = Address.objects.get(id = created_address_pk)
            customer = Customer.objects.get(user_id=request.user.id)
            customer_address = Customer_Address(address_id=address, customer_id=customer)
            customer_address.save()
            note = 'New address successfully added'
            # new_form = AddressForm()
            return render(request, 'account/add_address.html', {'note':note, 'customer_id':customer_id})
            # return render(request, 'registration/user-profile.html', {'note':note})
        else:
            note = 'Error adding address'
            address_form = AddressForm()
            return render(request, 'account/add_address.html', {'customer_id':customer_id, 'note':note, 'form':address_form})
    else:
       address_form = AddressForm()
       return render(request, 'account/add_address.html', {'customer_id':customer_id, 'form':address_form})

def delete_address(request, address_id):
    address = Address.objects.get(id=address_id)
    address.delete()
    customer = Customer.objects.get(user_id = request.user.id)
    customer_addresses = list(Customer_Address.objects.filter(customer_id_id=customer.id))
    addresses = []
    for cust_add in customer_addresses:
        addresses.append(Address.objects.get(id = cust_add.address_id_id))
    return render(request, 'account/user-profile.html', {'customer':customer, 'addresses':addresses})

def edit_address(request, address_id):
    address = Address.objects.get(pk=address_id)
    form = AddressForm(instance = address)
    if request.method == 'POST':
        filled_form = AddressForm(request.POST, instance=address)
        if filled_form.is_valid():
            filled_form.save()
            form = filled_form
            note = 'Your info has been successfully changed'
            return render(request, 'account/edit_address.html', {'form':form, 'note':note, 'address':address})
    return render(request, 'account/edit_address.html', {'form':form, 'address':address})

def edit_cuisine(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    if request.method == 'POST':
        all_cuisines = Cuisine.objects.all()
        for item in all_cuisines:
            if request.POST.get('c' + str(item.id)) == 'clicked':
                if not Customer_Cuisine.objects.filter(customer_id_id=customer.id, cuisine_id_id=item.id).exists():
                    new_cust_cuisine = Customer_Cuisine(customer_id_id=customer.id, cuisine_id_id=item.id)
                    new_cust_cuisine.save()
            else:
                if Customer_Cuisine.objects.filter(customer_id_id=customer.id, cuisine_id_id=item.id).exists():
                    old_cust_cuisine = Customer_Cuisine.objects.filter(customer_id_id=customer.id, cuisine_id_id=item.id)
                    old_cust_cuisine.delete()
        # return render(request, 'account/edit_cuisine.html')
    non_cuisines = list(Cuisine.objects.all())
    cust_cuisines = list(Customer_Cuisine.objects.filter(customer_id_id=customer.id))
    cuisines = []
    for cust_cuis in cust_cuisines:
        cuisines.append(Cuisine.objects.get(id = cust_cuis.cuisine_id_id))
    for cuisine in non_cuisines:
        if cuisine in cuisines:
            non_cuisines.remove(cuisine)
    return render(request, 'account/edit_cuisine.html', {'customer':customer, 'non_cuisines':non_cuisines, 'cuisines':cuisines});

def cart(request):
    return render(request, 'tables/cart.html')

@login_required
def add_to_cart(request, id):
    item = get_object_or_404(Item, id=id)
    customer = Customer.objects.get(user_id = request.user.id)
    order_item, exist = OrderItem.objects.get_or_create(
        item = item,
        customer = customer,
        ordered = False
    )
    print()
    print(customer)
    print(order_item.quantity)
    print(item)
    print()
    order = Order.objects.filter(customer=customer, ordered=False)
    print(order)
    if order.exists():
        possible_order_orderitems = list(Order_OrderItem.objects.filter(order=order))
        print(possible_order_orderitems)
        for order_orderitem in possible_order_orderitems:
            order_item = order_orderitem.order_item
            if order_item.item == item:
                order_item.quantity += 1
                order_item.save()
                return render(request, 'tables/cart.html')
            else:
                new_order_orderitem = Order_OrderItem(order_item=order_item, order=order)
                new_order_orderitem.save()
                return render(request, 'tables/cart.html')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            customer=customer,
            ordered_date=ordered_date
        )
        new_order_orderitem = Order_OrderItem(order_item=order_item, order=order)
        new_order_orderitem.save()
        return render(request, 'tables/cart.html')

def checkout(request):
    form = OrderInfoForm()
    context = {
    'form': form,
    }
    return render(request, 'tables/checkout.html', context = context)

def confirmation(request):
    deliveryEmployeeName = "John Doe"
    deliveryEmployeePhone = "2291824093"
    OrderNumber = 0
    OrderNumber = OrderNumber + 1
    context = {
    'deliveryEmployeeName': deliveryEmployeeName,
    'deliveryEmployeePhone': deliveryEmployeePhone,
    'OrderNumber': OrderNumber
    }
    return render(request, 'tables/confirmation.html', context = context)

def join(request):
    return render(request, 'tables/join.html')
