from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import (CustomSignupForm, CustomerForm, AddressForm,
CheckoutForm, PaymentForm)

from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
import stripe
import googlemaps
import json
import random
import string
from django.http import HttpRequest
from decouple import config
from decimal import *

from .models import Restaurant, Menu, Item, Cuisine, Customer_Cuisine, Order, OrderItem, Order_OrderItem
from .models import Address, Customer, Customer_Address, Restaurant_Cuisine, Payment, Review

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
    if address_str is '':
        context = {
        'num_of_items': getCartSize(request),
        'message': 'Please enter a valid location for your search.'
        }
        return render (request, 'tables/home.html', context=context)
    restaurants = Restaurant.objects.all()
    restaurant_dists = {}
    distance_list = []
    if request.user.is_authenticated:
        customer = Customer.objects.get(user_id = request.user.id)
        restaurant_cuisines = {}
        customer_cuisines = get_list_of_customer_cuisines(customer)
    distance_list = []
        # common_list = []
    for restaurant in restaurants:
        my_dist = gmaps.distance_matrix(address_str, restaurant.address, units='imperial')['rows'][0]['elements'][0]
        print(my_dist)
        if my_dist['status'] is not 'OK':
            context = {
            'num_of_items': getCartSize(request),
            'message': 'Please enter a valid location for your search.'
            }
            return render (request, 'tables/home.html', context=context)
        restaurant_dists[restaurant.name + ' text'] = my_dist['distance']['text'] + 'les'
        restaurant_dists[restaurant.name + ' value'] = my_dist['distance']['value']
        distance_list.append(restaurant_dists[restaurant.name + ' value'])
        # print('restaurant_dist:', restaurant_dists[restaurant.name + ' value'])
        if request.user.is_authenticated:
            restaurant_cuisines[restaurant.name + ' cuisines'] = get_list_of_restaurant_cuisines(restaurant)
            # num_common = get_num_common_cuisines(customer, restaurant)
            # common_list.append(num_common)
            # print('Common cuisines: ', num_common)
    print(restaurant_dists)
    # print('common list: ', common_list)
    # restaurants_sorted_by_common = [x for _,x in sorted(zip(common_list,restaurants))]
    restaurants = [x for _,x in sorted(zip(distance_list,restaurants))]

    # restaurants.sort(key=lambda (x,y): restaurant_dists.index(x))
    context = {
    'restaurants':restaurants,
    'restaurant_dists':restaurant_dists,
    'num_of_items': getCartSize(request),
    }
    if request.user.is_authenticated:
        context['restaurant_cuisines'] = restaurant_cuisines
        context['customer_cuisines'] = customer_cuisines
    return render(request, 'tables/dashboard.html', context = context)

    @register.filter
    def get_item(dictionary, key):
            return dictionary.get(key)

def get_num_common_cuisines(customer, restaurant):
    customer_cuisines = get_list_of_customer_cuisines(customer)
    restaurant_cuisines = get_list_of_restaurant_cuisines(restaurant)
    num_common = 0
    for cuisine in customer_cuisines:
        if cuisine in restaurant_cuisines:
            num_common += 1
    return num_common

def restaurantView(request, restaurant_id):
    context = load_restaurant_view(restaurant_id)
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
        cuisines_str = ""
        for rest_cuis in rest_cuisines:
            cuisines_str = cuisines_str + " " + Cuisine.objects.get(id = rest_cuis.cuisine_id_id).name + ","
        cuisines_str = cuisines_str[:len(cuisines_str)-1]
    context = {
    'restaurant':restaurant,
    'menu_names':menu_names,
    'menu_items':menu_items,
    'i_amt':range(len(menu_names)),
    'cuisines_str':cuisines_str,
    'avg_stars': get_avg_stars(restaurant_id),
    'message':"",
    'num_of_items': getCartSize(request),
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
    'num_of_items': getCartSize(request),
    }
    return render(request, 'account/user-profile.html', context=context)

def order_history(request):
    customer = Customer.objects.get(user_id = request.user.id)
    order_list = []
    raw_order_list = list(Order.objects.filter(customer_id=customer.id, ordered=True))
    print(raw_order_list)
    for order in raw_order_list:
        print(order)
        order_items = get_list_of_order_items(order)
        subtotal = order.get_subtotal()
        fees = getFees(order)
        total = float(subtotal + fees["Sales Tax"] + fees["Shipping Fee"] + fees["Service Fee"])
        order_details = [order, order_items, total]
        order_list.append(order_details)
    context = {
    'num_of_items': getCartSize(request),
    'order_list':order_list,
    }
    return render(request, 'account/order_history.html', context=context)

def get_avg_stars(restaurant_id):
    review_list = list(Review.objects.filter(restaurant_id=restaurant_id))
    if len(review_list) != 0:
        avg = 0.0
        for review in review_list:
            avg += review.stars
        avg /= len(review_list)
        return avg
    else:
        return 0

def review(request, order_id):
    order = Order.objects.get(id=order_id)
    context = {
    'num_of_items': getCartSize(request),
    'id':order_id,
    'restaurant': order.restaurant.name,
    }
    if request.method == 'POST':
        stars = request.POST['stars']
        header = request.POST['header']
        text = request.POST['text']
        review = Review()
        if order.review != None and order.review != '':
            review = order.review
            review.stars = order.stars
            review.header=header
            review.customer_id = order.customer
            review.restaurant_id = order.restaurant
            if text:
                review.text = text
            else:
                review.text = ''
            review.save()
        else:
            review = Review(
            stars=stars,
            header=header,
            customer_id = order.customer,
            restaurant_id = order.restaurant
            )
            if text:
                review.text=text
            else:
                review.text = ''
        review.save()
        order.review = review
        order.save()
        context['note'] = 'Your review has been saved'
    review = order.review
    if review:
        context['stars'] = review.stars
        context['header'] = review.header
        context['text'] = review.text
    return render(request, 'account/review.html', context=context)

def restaurant_review(request, restaurant_id):
    review_list = list(Review.objects.filter(restaurant_id=restaurant_id))
    context = {
    'num_of_items': getCartSize(request),
    'restaurant_id': restaurant_id,
    'review_list': review_list,
    }
    return render(request, 'tables/restaurant_review.html', context=context)

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
    'accountCreation': True
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
    'form': form,
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
            address.type = 'S'
            address.save()
            customer = Customer.objects.get(user_id=request.user.id)
            customer_address = Customer_Address(address_id=address, customer_id=customer)
            customer_address.save()
        else:
            created_address_pk = None
        context = {
        'created_address_pk':created_address_pk,
        # 'accountCreation': True
        }
        return render(request, 'tables/home.html', context=context)

def add_address(request, customer_id):
    context = {
    'customer_id':customer_id,
    'num_of_items': getCartSize(request),
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
            'address':address,
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
    'cuisines':cuisines,
    }
    return render(request, 'account/edit_cuisine.html', context=context)

def get_list_of_order_items(order):
    order_items = []
    bridgeItems = list(Order_OrderItem.objects.filter(order_id=order.id))
    for bridge_item in bridgeItems:
        item = OrderItem.objects.get(pk=bridge_item.order_item.id)
        order_items.append(item)
    return order_items

def get_list_of_restaurant_cuisines(restaurant):
    restaurant_cuisines = []
    bridgeItems = list(Restaurant_Cuisine.objects.filter(restaurant_id_id=restaurant.id))
    print('rest_cuisines bridgeItem: ',len(bridgeItems))
    for bridge_item in bridgeItems:
        cuisine = Cuisine.objects.get(pk=bridge_item.cuisine_id.id)
        restaurant_cuisines.append(cuisine)
    return restaurant_cuisines

def get_list_of_customer_cuisines(customer):
    customer_cuisines = []
    bridgeItems = list(Customer_Cuisine.objects.filter(customer_id_id=customer.id))
    print('customer_cusines bridgeItem: ',len(bridgeItems))
    for bridge_item in bridgeItems:
        cuisine = Cuisine.objects.get(pk=bridge_item.cuisine_id.id)
        customer_cuisines.append(cuisine)
    return customer_cuisines

def get_cart_subtotal(cart):
    subtotal = 0
    item_list = cart.get('details').get('item_id_list')
    for item_id in item_list:
        item_price = cart.get(str(item_id)).get('item').get('price')
        item_quantity =  cart.get(str(item_id)).get('quantity')
        subtotal += float(item_price) * item_quantity
    subtotal = Decimal(subtotal).quantize(Decimal('0.01'))
    return subtotal

def session_cart(request):
    context = {}
    cart = request.session.get('cart')
    if cart:
        restaurant = Restaurant.objects.get(id=cart.get('details').get('restaurant_id'))
        context = {
        'guest_user': True,
        'restaurant': restaurant
        }
        if request.method == 'POST':
            print(request.POST)
            item_list = cart.get('details').get('item_id_list')
            for item_id in item_list:
                if ('item_note' + str(item_id)) in request.POST:
                    item_note = request.POST['item_note' + str(item_id)]
                    cart[str(item_id)]['note'] = item_note
                if ('quantity' + str(item_id)) in request.POST:
                    quantity = int(request.POST['quantity' + str(item_id)])
                    if quantity == 0:
                        cart.pop(str(item_id))
                        item_list.remove(item_id)
                    else:
                        item = cart.get(str(item_id))
                        item['quantity'] = quantity
                        cart[str(item_id)] = item
            cart['details']['item_id_list'] = item_list
            if 'instructionBox' in request.POST:
                order_note = request.POST['instructionBox']
                cart['details']['note'] = order_note
            request.session['cart'] = cart
            print('New Cart:\n', cart)
        cart_size = getCartSize(request)
        context['num_of_items'] = cart_size
        if cart_size < 1:
            request.session.pop('cart')
            context = {
            'message': 'You do not have a pending order',
            'num_of_items': 0,
            }
            return context
        context['order_subtotal'] = get_cart_subtotal(cart)
        item_ids = cart.get('details').get('item_id_list')
        order_items = []
        for id in item_ids:
            item = Item.objects.get(id=id)
            item_dict = {
            'item': item,
            'quantity': cart.get(str(item.id)).get('quantity')
            }
            if cart.get(str(item.id)).get('note'):
                item_dict['note'] = cart.get(str(item.id)).get('note')
            print('ITEM DICT FOR ', id, ": ", item_dict)
            order_items.append(item_dict)
        if cart.get('details').get('note'):
            context['order_note'] = cart.get('details').get('note')
        context['order_items'] = order_items
    else:
        context['message'] = "You do not have a pending order"
    return context

def delete_order(order):
    bridge_items = list(Order_OrderItem.objects.filter(order=order))
    for bridge_item in bridge_items:
        item = Item.objects.get(id=bridge_items.order_item.id)
        item.delete()
    order.delete()

def cart(request):
    context = {}
    if request.user.id:
        customer = Customer.objects.get(user_id = request.user.id)
        context = {
        'restaurant': getOrderRestaurant(request)
        }
        order_qs = Order.objects.filter(customer_id=customer.id, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            order_items = get_list_of_order_items(order)
            if request.method == 'POST':
                for order_item in order_items:
                    if ('item_note' + str(order_item.id)) in request.POST:
                        item_note = request.POST['item_note'+ str(order_item.id)]
                        order_item.note = item_note
                        order_item.save()
                    if ('quantity' + str(order_item.id)) in request.POST:
                        quantity = int(request.POST['quantity'+ str(order_item.id)])
                        if quantity == 0:
                            order_item.delete()
                        else:
                            order_item.quantity = quantity
                            order_item.save()
                if 'instructionBox' in request.POST:
                    order_note = request.POST['instructionBox']
                    order.note = order_note
                    order.save()
            cart_size = getCartSize(request)
            context['num_of_items'] = cart_size
            if cart_size < 1:
                delete_order(order)
                context = {
                'message': 'You do not have a pending order',
                'num_of_items': 0
                }
                return render(request, 'tables/cart.html', context=context)
            context['order_subtotal'] =  order.get_subtotal()
            order_items = get_list_of_order_items(order)
            context['order'] =  order
            context['order_items'] =  order_items
        else:
            context['message'] = "You do not have a pending order"
    else:
        context = session_cart(request)
    return render(request, 'tables/cart.html', context=context)

def add_to_session_cart(request, id, restaurant_id):
    item = get_object_or_404(Item, id=id)
    quantity = int(request.POST['quantity'+ str(item.id)])
    restaurant = get_restaurant_of_item(item)
    cart = request.session.get('cart')
    if cart:
        # cart exists
        if cart.get('details').get('restaurant_id') == restaurant.id:
            order_item = cart.get(str(item.id))
            if order_item == None:
                # item does not exist in cart
                order_item_details = {
                'quantity': quantity,
                'item': item.get_dict_of_model(),
                }
                list = cart.get('details').get('item_id_list')
                list.append(str(item.id))
                cart['details']['item_id_list'] = list
                cart[str(item.id)] = order_item_details
            else:
                # item exists, update quantity
                prev_quantity = cart.get(str(item.id)).get('quantity')
                cart[str(item.id)]['quantity'] = prev_quantity + quantity
            request.session['cart'] = cart
            message = "Cart updated."
        else:
            # different restaurant
            message = "Items cannot be added to cart from multiple restaurants."
    else:
        # cart does not exist, create cart
        request.session['cart'] = {}
        order_details = {
        'restaurant_id': restaurant.id,
        'item_id_list': [item.id,],
        }
        order_item_details = {
        'quantity': quantity,
        'item': item.get_dict_of_model(),
        }
        request.session['cart']['details'] = order_details
        request.session['cart'][str(item.id)] = order_item_details
        message = "Cart updated."
    context = load_restaurant_view(restaurant_id)
    context['message'] = message
    context['num_of_items'] = getCartSize(request)
    print(request.session.get('cart'))
    return context

def add_to_cart(request, id, restaurant_id):
    context = {}
    if request.user.id:
        customer = Customer.objects.get(user_id = request.user.id)
        item = get_object_or_404(Item, id=id)
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
    else:
        context = add_to_session_cart(request, id, restaurant_id)
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

def get_bill_dict(cart):
    bill_dict = {}
    item_list = cart.get('details').get('item_id_list')
    for id in item_list:
        order_item = cart.get(str(id))
        total_price = float(order_item.get('item').get('price')) * float(order_item.get('quantity'))
        bill_dict[order_item.get('item').get('name')] = {
        'total_price': Decimal(total_price).quantize(Decimal('0.01')),
        'quantity': order_item.get('quantity'),
        }
    return bill_dict

def session_checkout(request):
    context = {}
    cart = request.session.get('cart')
    if cart:
        restaurant = Restaurant.objects.get(id=cart.get('details').get('restaurant_id'))
        subtotal = get_cart_subtotal(cart)
        fees = getFeesForGuestCart(subtotal)
        order_list = get_bill_dict(cart)
        form = CheckoutForm
        total = subtotal + fees["Sales Tax"] + fees["Shipping Fee"] + fees["Service Fee"]
        context = {
            'num_of_items': getCartSize(request),
            'restaurant':restaurant,
            'form': form,
            'fees': fees,
            'subtotal': subtotal,
            'order_list': order_list,
            'total': total,
            'guest_user': True,
        }
        if request.method == 'GET':
            return (context, True)
        elif request.method == 'POST':
            form = form = CheckoutForm(request.POST or None)
            if form.is_valid():
                print("Adding shipping address to cart")
                shipping_address = form.cleaned_data.get(
                    'shipping_address')
                shipping_city = form.cleaned_data.get(
                    'shipping_city')
                shipping_state = form.cleaned_data.get(
                    'shipping_state')
                shipping_zip = form.cleaned_data.get('shipping_zip')
                if is_valid_form([shipping_address, shipping_city, shipping_state, shipping_zip]):
                    print("new shipping address was valid")
                    cart_shipping_address = {
                    'nickname': 'Shipping Address',
                    'street': shipping_address,
                    'city': shipping_city,
                    'state': shipping_state,
                    'zipcode': shipping_zip,
                    'address_type': 'S',
                    }
                    cart['details']['shipping_address'] = cart_shipping_address
                else:
                    context['note'] = "Please fill in the required shipping address fields"
                    return (context, False)
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')
                if same_billing_address:
                    print("bill add = ship add")
                    cart_billing_address = cart.get('details').get('shipping_address')
                    cart['details']['billing_address'] = cart_billing_address
                else:
                    print("Adding different billing address to cart")
                    billing_address = form.cleaned_data.get(
                        'billing_address')
                    billing_city = form.cleaned_data.get(
                        'billing_city')
                    billing_state = form.cleaned_data.get(
                        'billing_state')
                    billing_zip = form.cleaned_data.get('billing_zip')
                    if is_valid_form([billing_address, billing_city, billing_state, billing_zip]):
                        print("new billing address was valid")
                        cart_billing_address = {
                        'nickname': 'Billing Address',
                        'street': billing_address,
                        'city': billing_city,
                        'state': billing_state,
                        'zipcode': billing_zip,
                        'address_type': 'B',
                        }
                        cart['details']['billing_address'] = cart_billing_address
                    else:
                        context['note'] = "Please fill in the required billing address fields"
                        return (context, False)
            context['num_of_items'] = getCartSize(request)
            context['payment'] = PaymentForm()
            subtotal = get_cart_subtotal(cart)
            fees = getFeesForGuestCart(subtotal)
            context['total'] = subtotal + fees["Sales Tax"] + fees["Shipping Fee"] + fees["Service Fee"]
            context = load_payment(request, context)
            request.session['cart'] = cart
            return (context, True)
    else:
        context['note'] = "You do not have a pending order"
        return (context, False)

def checkout(request):
    context = {}
    if request.user.id:
        customer = Customer.objects.get(user_id = request.user.id)
        restaurant = getOrderRestaurant(request)
        order = ''
        context = {
            'num_of_items': getCartSize(request),
            'restaurant':restaurant,
        }
        if request.method == 'GET':
            try:
                order = Order.objects.get(customer_id=customer.id, ordered=False)
                fees = getFees(order)
                subtotal = order.get_subtotal()
                order_list = order.get_order_list()
                form = CheckoutForm()
                total = subtotal + fees["Sales Tax"] + fees["Shipping Fee"] + fees["Service Fee"]
                context['order'] = order
                context['form'] = form
                context['fees'] = fees
                context['subtotal'] = subtotal
                context['order_list'] = order_list
                context['total'] = total
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
                return render(request, "tables/checkout.html", context=context)
        elif request.method == 'POST':
            form = CheckoutForm(request.POST or None)
            print("\n\n")
            try:
                order = Order.objects.get(customer_id=customer.id, ordered=False)
                fees = getFees(order)
                subtotal = order.get_subtotal()
                order_list = order.get_order_list()
                total = subtotal + fees["Sales Tax"] + fees["Shipping Fee"] + fees["Service Fee"]
                context['order'] = order
                context['form'] = form
                context['fees'] = fees
                context['subtotal'] = subtotal
                context['order_list'] = order_list
                context['total'] = total
                order_list = order.get_order_list()
                context['order_list'] = order_list
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
                                order.billing_address = def_shipping_address
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
                    print("Reached the end\n\n")
            except Exception:
                context['note'] = "You do not have an active order"
                return render(request, "tables/checkout.html", context=context)
            context = {
                'num_of_items': getCartSize(request),
            }
            print(order)
            context = addOrderInfo(request, context, order)
            context = load_payment(request, context)
            return render(request, "tables/payment.html", context=context)
    else:
        context, post_success = session_checkout(request)
        if post_success and request.method == 'POST':
            context['guest_user'] = True
            return render(request, "tables/payment.html", context=context)
        else:
            return render(request, "tables/checkout.html", context=context)

def confirmation(request):
    context = {
    'note': 'Go order some munchies!',
    }
    return render(request, 'tables/confirmation.html', context = context)

def getCartSize(request):
    num_of_items = -1
    if request.user.id:
        customer = Customer.objects.get(user_id = request.user.id)
        order_qs = Order.objects.filter(customer_id=customer.id, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            num_of_items = order.get_total_quantity()
    else:
        if request.session.get('cart'):
            num_of_items = get_cart_size(request.session.get('cart'))
    return num_of_items

def get_cart_size(cart):
    size = 0
    item_list = cart.get('details').get('item_id_list')
    for item_id in item_list:
        item_quantity =  cart.get(str(item_id)).get('quantity')
        size += item_quantity
    return size

def getOrderRestaurant(request):
    restaurant = ""
    customer_exists = Customer.objects.filter(user_id = request.user.id).exists()
    if customer_exists:
        customer = Customer.objects.get(user_id = request.user.id)
        order_qs = Order.objects.filter(customer_id=customer.id, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            restaurant = order.restaurant
    return restaurant

def getFees(order):
    fees = {
    "Sales Tax": order.get_sales_tax(),
    "Shipping Fee": Decimal('10.00'),
    "Service Fee": Decimal('5.00')
    }
    return fees

def getFeesForGuestCart(subtotal):
    fees = {
    "Sales Tax": Decimal(float(subtotal) * 0.09).quantize(Decimal('0.01')),
    "Shipping Fee": Decimal('10.00'),
    "Service Fee": Decimal('5.00')
    }
    return fees

def addOrderInfo(request, context, order):
    context['payment'] = PaymentForm()
    subtotal = order.get_subtotal()
    fees = getFees(order)
    context['total'] = subtotal + fees["Sales Tax"] + fees["Shipping Fee"] + fees["Service Fee"]
    return context

def save_cart_as_order(cart, payment):
    restaurant = Restaurant.objects.get(id=cart.get('details').get('restaurant_id'))
    shipping_address = Address(
    nickname = cart.get('details').get('shipping_address').get('nickname'),
    street = cart.get('details').get('shipping_address').get('street'),
    city = cart.get('details').get('shipping_address').get('city'),
    state = cart.get('details').get('shipping_address').get('state'),
    zipcode = cart.get('details').get('shipping_address').get('zipcode'),
    address_type = cart.get('details').get('shipping_address').get('address_type'),
    )
    shipping_address.save()
    billing_address = Address(
    nickname = cart.get('details').get('billing_address').get('nickname'),
    street = cart.get('details').get('billing_address').get('street'),
    city = cart.get('details').get('billing_address').get('city'),
    state = cart.get('details').get('billing_address').get('state'),
    zipcode = cart.get('details').get('billing_address').get('zipcode'),
    address_type = cart.get('details').get('billing_address').get('address_type'),
    )
    billing_address.save()
    note = cart.get('details').get('note')
    order = Order(
    ref_code = create_ref_code(),
    start_date = timezone.now(),
    ordered_date = timezone.now(),
    ordered = True,
    restaurant = restaurant,
    shipping_address = shipping_address,
    billing_address = billing_address,
    note = note,
    payment = payment,
    )
    order.save()
    id_list = cart.get('details').get('item_id_list')
    for id in id_list:
        item = Item.objects.get(id=id)
        order_item = OrderItem(
        ordered = True,
        item = item,
        quantity = cart.get(str(id)).get('quantity'),
        note = cart.get(str(id)).get('note')
        )
        order_item.save()
        bridge_item = Order_OrderItem(
        order = order,
        order_item = order_item
        )
        bridge_item.save()
    return order

def load_payment(request, context):
    if request.user.id:
        customer = Customer.objects.get(user_id = request.user.id)
        order = Order.objects.get(customer_id=customer.id, ordered=False)
        if order.billing_address:
            if customer.stripeid != '' and customer.stripeid is not None:
                cards = stripe.Customer.list_sources(
                    customer.stripeid,
                    limit=3,
                    object='card'
                )
                print(cards)
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return context
        else:
            context['note'] = "You have not added a billing address"
            return context
    else:
        if not request.session.get('cart').get('details').get('billing_address'):
            context['note'] = "You have not added a billing address"
        return context

def session_payment(request):
    cart = request.session['cart']
    context = {
        'num_of_items': getCartSize(request),
    }
    if request.method == 'GET':
        context = load_payment(request, context)
        return (context, True)
    elif request.method == 'POST':
        form = PaymentForm(request.POST)
        print(request)
        print(request.POST)
        if form.is_valid():
            print("ok")
            token = form.cleaned_data.get('stripeToken')

            subtotal = get_cart_subtotal(cart)
            fees = getFeesForGuestCart(subtotal)
            total = subtotal + fees["Sales Tax"] + fees["Shipping Fee"] + fees["Service Fee"]
            context['subtotal'] = subtotal
            context['fees'] = fees
            amount = total * 100
            print("Calc amt: " + str(amount))
            print("Calc total: " + str(total))

            try:
                # charge once off on the token
                charge = stripe.Charge.create(
                    amount=int(amount),  # cents
                    currency="usd",
                    source=token
                )
                print("charging the one time card token")

                # create the payment
                payment = Payment()
                print("payment created")
                payment.stripe_charge_id = charge['id']
                print("set stripe charge id")
                payment.amount = float(total)
                print(payment)
                payment.save()
                print("payment saved")

                new_order = save_cart_as_order(cart, payment)
                print("payment assigned to order")
                print('Final Cart:', cart)
                request.session.pop('cart')
                print('Removed? ', request.session.get('cart'))

                context['num_of_items'] = 0
                context['order_ref'] = new_order.ref_code
                context['deliveryEmployeeName'] = 'Jennifer'
                context['deliveryEmployeePhone'] = '909-436-3333'
                return (context, True)

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                context['note'] = f"{err.get('message')}"
                return (context, False)

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                context['note'] = "Rate limit error"
                return (context, False)

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                context['note'] = "Invalid parameters"
                return (context, False)

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                context['note'] = "Not authenticated"
                return (context, False)

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")
                context['note'] = "Not authenticated"
                return (context, False)

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                context['note'] = "Something went wrong. You were not charged. Please try again."
                return (context, False)

            # except Exception as e:
            #     # send an email to ourselves
            #     context['note'] = "A serious error occurred. We have been notifed."
            #     return (context, False)

        context['note'] = "Invalid data received"
        return (context, False)

def payment(request):
    if request.user.id:
        customer = Customer.objects.get(user_id = request.user.id)
        order = Order.objects.get(customer_id=customer.id, ordered=False)
        context = {
            'num_of_items': getCartSize(request),
        }
        if request.method == 'GET':
            context = load_payment(request, context)
            return render(request, "tables/payment.html", context=context)
        elif request.method == 'POST':
            form = PaymentForm(request.POST)
            print(request)
            print(request.POST)
            if form.is_valid():
                print("ok")
                token = form.cleaned_data.get('stripeToken')
                save = form.cleaned_data.get('save')
                use_default = form.cleaned_data.get('use_default')

                if save:
                    if customer.stripeid != '' and customer.stripeid is not None:
                        stripeCustomer = stripe.Customer.retrieve(
                            customer.stripeid)
                        stripeCustomer.sources.create(source=token)
                        print("Used previous stripe id")

                    else:
                        stripeCustomer = stripe.Customer.create(
                            email=request.user.email,
                        )
                        stripeCustomer.sources.create(source=token)
                        customer.stripeid = stripeCustomer['id']
                        customer.save()
                        print("Created new stripe id")

                subtotal = order.get_subtotal()
                fees = getFees(order)
                context['subtotal'] = subtotal
                context['fees'] = fees
                context['total'] = subtotal + fees["Sales Tax"] + fees["Shipping Fee"] + fees["Service Fee"]

                total = float(subtotal + fees["Sales Tax"] + fees["Shipping Fee"] + fees["Service Fee"])
                amount = total * 100
                print("Calc amt: " + str(amount))
                print("Calc total: " + str(total))

                try:
                    if use_default or save:
                        # charge the stripeCustomer because we cannot charge the token more than once
                        charge = stripe.Charge.create(
                            amount=int(amount),  # cents
                            currency="usd",
                            customer=customer.stripeid
                        )
                        print("charging the recurring customer")
                    else:
                        # charge once off on the token
                        charge = stripe.Charge.create(
                            amount=int(amount),  # cents
                            currency="usd",
                            source=token
                        )
                        print("charging the one time card token")

                    # create the payment
                    payment = Payment()
                    print("payment created")
                    payment.stripe_charge_id = charge['id']
                    print("set stripe charge id")
                    payment.customer = customer
                    print("created customer")
                    payment.amount = total
                    print(payment)
                    payment.save()
                    print("payment saved")

                    # assign the payment to the order
                    order_items = get_list_of_order_items(order)
                    print(order_items)
                    for item in order_items:
                        item.ordered = True

                    # order_items.update(ordered=True)
                    print(order_items)
                    for item in order_items:
                        item.save()
                    print("payment assigned to order items")

                    order.ordered = True
                    order.payment = payment
                    order.ref_code = create_ref_code()
                    order.save()
                    print("payment assigned to order")

                    context['num_of_items'] = 0
                    context['order_ref'] = order.ref_code
                    context['deliveryEmployeeName'] = 'Jennifer'
                    context['deliveryEmployeePhone'] = '909-436-3333'
                    return render(request, "tables/confirmation.html", context=context)

                except stripe.error.CardError as e:
                    body = e.json_body
                    err = body.get('error', {})
                    context['note'] = f"{err.get('message')}"
                    return render(request, "tables/payment.html", context=context)

                except stripe.error.RateLimitError as e:
                    # Too many requests made to the API too quickly
                    context['note'] = "Rate limit error"
                    return render(request, "tables/payment.html", context=context)

                except stripe.error.InvalidRequestError as e:
                    # Invalid parameters were supplied to Stripe's API
                    print(e)
                    context['note'] = "Invalid parameters"
                    return render(request, "tables/payment.html", context=context)

                except stripe.error.AuthenticationError as e:
                    # Authentication with Stripe's API failed
                    # (maybe you changed API keys recently)
                    context['note'] = "Not authenticated"
                    return render(request, "tables/payment.html", context=context)

                except stripe.error.APIConnectionError as e:
                    # Network communication with Stripe failed
                    messages.warning(self.request, "Network error")
                    return redirect("/")
                    context['note'] = "Not authenticated"
                    return render(request, "tables/payment.html", context=context)

                except stripe.error.StripeError as e:
                    # Display a very generic error to the user, and maybe send
                    # yourself an email
                    context['note'] = "Something went wrong. You were not charged. Please try again."
                    return render(request, "tables/payment.html", context=context)

                except Exception as e:
                    # send an email to ourselves
                    context['note'] = "A serious error occurred. We have been notifed."
                    return render(request, "tables/payment.html", context=context)

            context['note'] = "Invalid data received"
            return render(request, "tables/payment.html", context=context)
    else:
        context, post_success = session_payment(request)
        if post_success and request.method == 'POST':
            return render(request, "tables/confirmation.html", context=context)
        else:
            return render(request, "tables/payment.html", context=context)

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
