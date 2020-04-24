from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import CustomSignupForm, CustomerForm, AddressForm, CheckoutForm
from .forms import BillingCheckout, DeliveryCheckout

from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
import stripe
import googlemaps
import json
from django.http import HttpRequest
from decouple import config
from decimal import *

from .models import Restaurant, Menu, Item, Cuisine, Customer_Cuisine, Order, OrderItem, Order_OrderItem
from .models import Address, Customer, Customer_Address, Restaurant_Cuisine

stripe.api_key = config('STRIPE_API_KEY')
gmaps = googlemaps.Client(key=config('GOOGLE_API_KEY'))

def home(request):
    context = {
    'num_of_items': getCartSize(request),
    }
    return render (request, 'tables/home.html', context=context)

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
    'num_of_items': getCartSize(request),
    }
    return render(request, 'tables/dashboard.html', context = context)

def restaurantView(request, restaurant_id):
    context = load_restaurant_view(restaurant_id)
    context['num_of_items'] = getCartSize(request)
    return render(request, 'tables/restaurant_view.html',context = context)

def load_restaurant_view(restaurant_id):
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
    context = {
    'restaurant':restaurant,
    'menu_names':menu_names,
    'menu_items':menu_items,
    'i_amt':range(len(menu_names)),
    'cuisines_str':cuisines_str,
    'message':"",
    }
    return context

def getListOfAddresses(customer):
    customer_addresses = list(Customer_Address.objects.filter(customer_id=customer))
    addresses = []
    print(customer_addresses)
    for cust_add in customer_addresses:
        addresses.append(Address.objects.get(id = cust_add.address_id_id))
    return addresses

def profile(request):
    customer = Customer.objects.get(user_id = request.user.id)
    addresses = getListOfAddresses(customer.id)
    cust_cuisines = list(Customer_Cuisine.objects.filter(customer_id_id=customer.id))
    cuisines = []
    for cust_cuis in cust_cuisines:
        cuisines.append(Cuisine.objects.get(id = cust_cuis.cuisine_id_id))
    context = {
    'customer': customer,
    'addresses': addresses,
    'cuisines': cuisines,
    'num_of_items': getCartSize(request)
    }
    return render(request, 'account/user-profile.html', context=context)

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
    context = {
    'num_of_items': getCartSize(request),
    }
    if request.method == 'POST':
        filled_form = CustomerForm(request.POST)
        if filled_form.is_valid():
            created_customer = filled_form.save(commit=False)
            created_customer.user = request.user
            created_customer.save()
            created_customer_pk = created_customer.id
            address_form = AddressForm()
            context['form'] = address_form
            context['created_customer_pk'] = created_customer_pk
            return render(request, 'registration/address.html', context=context)
        else:
            note = 'Form not valid. Please try again'
            customer_form = CustomerForm()
            context['form'] = customer_form
            context['note'] = note
            return render(request, 'registration/customer-registration.html', context=context)
    else:
        customer_form = CustomerForm()
        context['form'] = customer_form
        return render(request, 'registration/customer-registration.html', context=context)

def edit_customer(request):
    customer = Customer.objects.get(user_id=request.user.id)
    form = CustomerForm(instance = customer)
    context = {
    'num_of_items': getCartSize(request),
    'form': form
    }
    if request.method == 'POST':
        filled_form = CustomerForm(request.POST, instance=customer)
        if filled_form.is_valid():
            filled_form.save()
            form = filled_form
            note = 'Your info has been successfully changed'
        else:
            note = 'There was an error in changing your information'
        context['note'] = note
        context['form'] = form
        return render(request, 'account/edit_customer.html', context=context)
    return render(request, 'account/edit_customer.html', context=context)

def fillAddress(request):
        filled_form = AddressForm(request.POST)
        if filled_form.is_valid():
            created_address = filled_form.save()
            created_address_pk = created_address.id
            filled_form = AddressForm()
            address = Address.objects.get(id = created_address_pk)
            address.default = True
            address.save()
            customer = Customer.objects.get(user_id=request.user.id)
            customer_address = Customer_Address(address_id=address, customer_id=customer)
            customer_address.save()
        else:
            created_address_pk = None
        context = {
        'created_address_pk':created_address_pk,
        'num_of_items': getCartSize(request)
        }
        return render(request, 'tables/home.html', context=context)

def add_address(request, customer_id):
    context = {
    'customer_id':customer_id,
    'num_of_items': getCartSize(request)
    }
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
            context['note'] = note
            return render(request, 'account/add_address.html', context=context)
        else:
            note = 'Error adding address'
            address_form = AddressForm()
            context['note'] = note
            context['form'] = address_form
            return render(request, 'account/add_address.html', context=context)
    else:
       address_form = AddressForm()
       context['form'] = address_form
       return render(request, 'account/add_address.html', context=context)

def delete_address(request, address_id):
    address = Address.objects.get(id=address_id)
    address.delete()
    customer = Customer.objects.get(user_id = request.user.id)
    customer_addresses = list(Customer_Address.objects.filter(customer_id_id=customer.id))
    addresses = []
    for cust_add in customer_addresses:
        addresses.append(Address.objects.get(id = cust_add.address_id_id))
    num_of_items = getCartSize(request)
    context = {
    'num_of_items': num_of_items,
    'customer':customer,
    'addresses':addresses
    }
    return render(request, 'account/user-profile.html', context=context)

def edit_address(request, address_id):
    address = Address.objects.get(pk=address_id)
    form = AddressForm(instance = address)
    num_of_items = getCartSize(request)
    if request.method == 'POST':
        filled_form = AddressForm(request.POST, instance=address)
        if filled_form.is_valid():
            filled_form.save()
            form = filled_form
            note = 'Your info has been successfully changed'
            context = {
            'num_of_items': num_of_items,
            'form':form,
            'note':note,
            'address':address
            }
            return render(request, 'account/edit_address.html', context=context)
    context = {
    'num_of_items': num_of_items,
    'form':form,
    'address':address
    }
    return render(request, 'account/edit_address.html', context=context)

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
    num_of_items = getCartSize(request)
    context = {
    'num_of_items': num_of_items,
    'customer':customer,
    'non_cuisines':non_cuisines,
    'cuisines':cuisines
    }
    return render(request, 'account/edit_cuisine.html', context=context)

def cart(request):
    #Order -> cart, contains OrderItems
    #OrderItem -> make up a Order(Cart), contains an Item plus other info (quantity, etc)
    #Order_OrderItem -> bridge table for the many to many relationship between Order and OrderItem
    #   -contains its own PK, an Order (pk), and an OrderItem (pk)
    context = {
    'num_of_items': getCartSize(request),
    'restaurant': getOrderRestaurant(request)
    }
    customer = Customer.objects.get(user_id = request.user.id)
    order_qs = Order.objects.filter(customer_id=customer.id, ordered=False)
    order_items = []
    if order_qs.exists():
        order = order_qs[0]
        context['order_subtotal'] =  order.get_subtotal()
        bridgeItems = list(Order_OrderItem.objects.filter(order_id=order.id))
        for bridge_item in bridgeItems:
            item = OrderItem.objects.get(pk=bridge_item.order_item.id)
            order_items.append(item)
    context['order_items'] =  order_items
    return render(request, 'tables/cart.html', context=context)

@login_required
def add_to_cart(request, id, restaurant_id):
    item = get_object_or_404(Item, id=id)
    customer = Customer.objects.get(user_id = request.user.id)
    quantity = int(request.POST['quantity'+ str(item.id)])
    restaurant = get_restaurant_of_item(item)
    order_item, created = OrderItem.objects.get_or_create(
        item = item,
        customer = customer,
        ordered = False,
    )
    order_qs = Order.objects.filter(customer_id=customer.id, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.restaurant == restaurant:
            if created == True:
                order_item.quantity = quantity
                order_item.save()
                new_order_orderitem = Order_OrderItem(order=order, order_item=order_item)
                new_order_orderitem.save()
            else:
                order_item.quantity += quantity
                order_item.save()
            message = "Cart updated."
        else:
            order_item.delete()
            message = "Items cannot be added to cart from multiple restaurants."
    else:
        # order does not exist, create order
        ordered_date = timezone.now()
        order = Order.objects.create(
            customer=customer,
            ordered_date=ordered_date,
            restaurant=restaurant
        )
        order_item.quantity = quantity
        order_item.save()
        new_order_orderitem = Order_OrderItem(order_item=order_item, order=order)
        new_order_orderitem.save()
        message = "Cart updated."
    context = load_restaurant_view(restaurant_id)
    context['message'] = message
    num_of_items = getCartSize(request)
    context['num_of_items'] = num_of_items
    return render(request, 'tables/restaurant_view.html',context = context)

def get_restaurant_of_item(item):
    menu = Menu.objects.get(id = item.menu_id_id)
    restaurant = Restaurant.objects.get(id = menu.restaurant_id_id)
    return restaurant

def getDefaultAddressOfType(addresses, type):
    for address in addresses:
        if (address.address_type == type) and (address.default == True):
            return address
    return None

def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

def checkout(request):
    customer = Customer.objects.get(user_id = request.user.id)
    billing = BillingCheckout()
    delivery = DeliveryCheckout()
    subtotal = getSubtotal(request)
    restaurant = getOrderRestaurant(request)
    order_list = getOrderList(request)
    fees = getFees(request)
    total = subtotal + fees["Sales Tax"] + fees["Shipping Fee"] + fees["Service Fee"]
    context = {
        'num_of_items': getCartSize(request),
        'billing':billing,
        'delivery':delivery,
        'order_list':order_list,
        'subtotal':subtotal,
        'restaurant':restaurant,
        'fees':fees,
        'total':total
    }
    if request.method == 'GET':
        try:
            order = Order.objects.get(customer_id=customer.id, ordered=False)
            form = CheckoutForm()
            context['order'] = order
            context['form'] = form
            all_addresses = getListOfAddresses(customer)
            def_shipping_address = getDefaultAddressOfType(all_addresses, 'S')
            if def_shipping_address != None:
                context['def_shipping_address'] = def_shipping_address
            def_billing_address = getDefaultAddressOfType(all_addresses, 'B')
            if def_billing_address != None:
                context['def_billing_address'] = def_billing_address
            return render(request, "tables/checkout.html", context)
        except ObjectDoesNotExist:
            context['note'] = "You do not have a pending order"
            return render(request, "checkout.html", context=context)
    elif request.method == 'POST':
        form = CheckoutForm(request.POST or None)
        print("\n\n")
        try:
            order = Order.objects.get(customer_id=customer.id, ordered=False)
            context['order'] = order
            context['form'] = form
            if form.is_valid():
                print("Valid form")
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                all_addresses = getListOfAddresses(customer.id)
                shipping_address = Address()
                if use_default_shipping:
                    print("Using the default shipping address")
                    def_shipping_address = getDefaultAddressOfType(all_addresses, 'S')
                    if def_shipping_address != None:
                        print("Saving the default shipping address")
                        order.shipping_address = def_shipping_address
                        order.save()
                    else:
                        context['note'] = "You do not have a default shipping address"
                        return render(request, "tables/checkout.html", context=context)
                else:
                    print("Saving a new shipping address")
                    shipping_address = form.cleaned_data.get(
                        'shipping_address')
                    shipping_city = form.cleaned_data.get(
                        'shipping_city')
                    shipping_state = form.cleaned_data.get(
                        'shipping_state')
                    shipping_zip = form.cleaned_data.get('shipping_zip')
                    if is_valid_form([shipping_address, shipping_city, shipping_state, shipping_zip]):
                        print("new default shipping address was valid")
                        shipping_address = Address(
                            nickname='Shipping Address',
                            street=shipping_address,
                            city=shipping_city,
                            state=shipping_state,
                            zipcode=shipping_zip,
                            address_type='S'
                        )
                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            print("new default shipping address should be new default")
                            def_shipping_address = getDefaultAddressOfType(all_addresses, 'S')
                            if def_shipping_address != None:
                                def_shipping_address.default = False
                                def_shipping_address.save()
                                print("old default shipping address reset")
                            shipping_address.default = True
                        shipping_address.save()
                        print("new default shipping address saved")
                        cust_add_bridge = Customer_Address(
                            address_id = shipping_address,
                            customer_id = customer
                        )
                        cust_add_bridge.save()
                        print("Saved bridge table item")
                        order.shipping_address = shipping_address
                        order.save()
                        print("order shipping add set")
                    else:
                        context['note'] = "Please fill in the required shipping address fields"
                        return render(request, "tables/checkout.html", context=context)
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')
                if same_billing_address:
                    print("bill add = ship add")
                    if use_default_shipping:
                        def_shipping_address = getDefaultAddressOfType(all_addresses, 'S')
                        if def_shipping_address != None:
                            print("bill add = default ship add")
                            order.shipping_address = def_shipping_address
                            order.save()
                    else:
                        print("bill add = new ship add")
                        order.billing_address = shipping_address
                        order.save()
                else:
                    use_default_billing = form.cleaned_data.get(
                        'use_default_billing')
                    if use_default_billing:
                        print("Using the default billing address")
                        def_billing_address = getDefaultAddressOfType(all_addresses, 'B')
                        if def_billing_address != None:
                            order.billing_address = def_billing_address
                            order.save()
                            print("order bill add set to def bill add")
                        else:
                            context['note'] = "You do not have a default billing address"
                            return render(request, "tables/checkout.html", context=context)
                    else:
                        print("Saving a new billing address")
                        billing_address = form.cleaned_data.get(
                            'billing_address')
                        billing_city = form.cleaned_data.get(
                            'billing_city')
                        billing_state = form.cleaned_data.get(
                            'billing_state')
                        billing_zip = form.cleaned_data.get('billing_zip')
                        if is_valid_form([billing_address, billing_city, billing_state, billing_zip]):
                            billing_address = Address(
                                nickname='Billing Address',
                                street=billing_address,
                                city=billing_city,
                                state=billing_state,
                                zipcode=billing_zip,
                                address_type='B'
                            )
                            set_default_billing = form.cleaned_data.get(
                                'set_default_billing')
                            if set_default_billing:
                                def_billing_address = getDefaultAddressOfType(all_addresses, 'B')
                                if def_billing_address != None:
                                    def_billing_address.default = False
                                    def_billing_address.save()
                                billing_address.default = True
                            billing_address.save()
                            cust_add_bridge = Customer_Address(
                                address_id = billing_address,
                                customer_id = customer
                            )
                            cust_add_bridge.save()
                            order.billing_address = billing_address
                            order.save()
                        else:
                            context['note'] = "Please fill in the required billing address fields"
                            return render(request, "tables/checkout.html", context=context)

                # payment_option = form.cleaned_data.get('payment_option')
                #
                # if payment_option == 'S':
                #     return redirect('core:payment', payment_option='stripe')
                # elif payment_option == 'P':
                #     return redirect('core:payment', payment_option='paypal')
                # else:
                #     messages.warning(
                #         self.request, "Invalid payment option selected")
                #     return redirect('core:checkout')
                context = {
                'num_of_items': getCartSize(request)
                }
                print("\n\n")
                return render(request, "tables/payment.html", context=context)
        except ObjectDoesNotExist:
            context['note'] = "You do not have an active order"
            return render(request, "tables/checkout.html", context=context)

def payment(request):
    return render(request, 'tables/payment.html')

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

def getCartSize(request):
    num_of_items = -1
    customer_exists = Customer.objects.filter(user_id = request.user.id).exists()
    if customer_exists:
        customer = Customer.objects.get(user_id = request.user.id)
        order_qs = Order.objects.filter(customer_id=customer.id, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            num_of_items = order.get_total_quantity()
    return num_of_items

def getOrderRestaurant(request):
    restaurant = ""
    customer_exists = Customer.objects.filter(user_id = request.user.id).exists()
    if customer_exists:
        customer = Customer.objects.get(user_id = request.user.id)
        order_qs = Order.objects.filter(customer_id=customer.id, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            restaurant = order.get_restaurant_name()
    return restaurant

def getSubtotal(request):
    subtotal = 0.0
    customer_exists = Customer.objects.filter(user_id = request.user.id).exists()
    if customer_exists:
        customer = Customer.objects.get(user_id = request.user.id)
        order_qs = Order.objects.filter(customer_id=customer.id, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            subtotal = order.get_subtotal()
    return subtotal

def getOrderList(request):
    order_list = 0.0
    customer_exists = Customer.objects.filter(user_id = request.user.id).exists()
    if customer_exists:
        customer = Customer.objects.get(user_id = request.user.id)
        order_qs = Order.objects.filter(customer_id=customer.id, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            order_list = order.get_order_list()
    return order_list

def getFees(request):
    fees = dict()
    customer_exists = Customer.objects.filter(user_id = request.user.id).exists()
    if customer_exists:
        customer = Customer.objects.get(user_id = request.user.id)
        order_qs = Order.objects.filter(customer_id=customer.id, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            fees = {
            "Sales Tax": order.get_sales_tax(),
            "Shipping Fee": Decimal('10.00'),
            "Service Fee": Decimal('5.00')
            }
    return fees
