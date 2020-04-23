from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import CustomSignupForm, CustomerForm, AddressForm, CheckoutForm
from .forms import NameCheckout, BillingCheckout, DeliveryCheckout

from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
import stripe
import googlemaps
import json
from django.http import HttpRequest
from decouple import config

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

def getListOfAddresses(customer_id):
    customer_addresses = list(Customer_Address.objects.filter(customer_id_id=customer_id))
    addresses = []
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
    num_of_items = getCartSize(request)
    context = {
    'num_of_items': num_of_items
    }
    return render(request, 'tables/cart.html', context=context)

@login_required
def add_to_cart(request, id, restaurant_id):
    item = get_object_or_404(Item, id=id)
    customer = Customer.objects.get(user_id = request.user.id)
    quantity = int(request.POST['quantity'+ str(item.id)])
    order_item, created = OrderItem.objects.get_or_create(
        item = item,
        customer = customer,
        ordered = False,
    )
    order_qs = Order.objects.filter(customer_id=customer.id, ordered=False)
    if order_qs.exists():
        if created == True:
            order = order_qs[0]
            order_item.quantity = quantity
            order_item.save()
            new_order_orderitem = Order_OrderItem(order=order, order_item=order_item)
            new_order_orderitem.save()
        else:
            order_item.quantity += quantity
            order_item.save()
    else:
        # order does not exist, create order
        ordered_date = timezone.now()
        order = Order.objects.create(
            customer=customer,
            ordered_date=ordered_date
        )
        order_item.quantity = quantity
        order_item.save()
        new_order_orderitem = Order_OrderItem(order_item=order_item, order=order)
        new_order_orderitem.save()
    context = load_restaurant_view(restaurant_id)
    context['message'] = "Cart updated."
    num_of_items = getCartSize(request)
    context['num_of_items'] = num_of_items
    return render(request, 'tables/restaurant_view.html',context = context)

def getFirstAddressOfType(addresses, type):
    for address in addresses:
        if address.address_type == type:
            return address

def checkout(request):
    customer = Customer.objects.get(user_id = request.user.id)
    if request.method == 'GET':
        try:
            order = Order.objects.get(customer_id=customer.id, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
                'num_of_items': getCartSize(request),
            }
            all_addresses = getListOfAddresses(customer.id)
            shipping_address = getFirstAddressOfType(all_addresses, 'S')
            # shipping_address_qs = Address.objects.filter(
            #     user=self.request.user,
            #     address_type='S',
            #     # default=True
            # )
            # if shipping_address_qs.exists():
                # context.update(
                #     {'default_shipping_address': shipping_address_qs[0]})

            billing_address = getFirstAddressOfType(all_addresses, 'B')
            # billing_address_qs = Address.objects.filter(
            #     user=self.request.user,
            #     address_type='B',
            #     default=True
            # )
            # if billing_address_qs.exists():
            #     context.update(
            #         {'default_billing_address': billing_address_qs[0]})
            context['shipping_address'] = shipping_address
            context['billing_address'] = billing_address
            return render(request, "tables/checkout.html", context)
        except ObjectDoesNotExist:
            context = {
            'num_of_items': getCartSize(request),
            'note': "You do not have an active order"
            }
            return render(request, "checkout.html", context=context)
    elif request.method == 'POST':
        form = CheckoutForm(request.POST or None)
        try:
            order = Order.objects.get(customer_id=customer.id, ordered=False)
            if form.is_valid():
                # use_default_shipping = form.cleaned_data.get(
                #     'use_default_shipping')
                # if use_default_shipping:
                #     print("Using the defualt shipping address")
                #     address_qs = Address.objects.filter(
                #         user=self.request.user,
                #         address_type='S',
                #         default=True
                #     )
                    # if address_qs.exists():
                    #     shipping_address = address_qs[0]
                    #     order.shipping_address = shipping_address
                    #     order.save()
                    # else:
                    #     messages.info(
                    #         self.request, "No default shipping address available")
                    #     return redirect('core:checkout')
                # else:
                #     print("User is entering a new shipping address")
                shipping_address1 = form.cleaned_data.get(
                    'shipping_address')
                shipping_address2 = form.cleaned_data.get(
                    'shipping_address2')
                # shipping_country = form.cleaned_data.get(
                #     'shipping_country')
                shipping_zip = form.cleaned_data.get('shipping_zip')
                #
                #     if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                #         shipping_address = Address(
                #             user=self.request.user,
                #             street_address=shipping_address1,
                #             apartment_address=shipping_address2,
                #             country=shipping_country,
                #             zip=shipping_zip,
                #             address_type='S'
                #         )
                #         shipping_address.save()
                #
                #         order.shipping_address = shipping_address
                #         order.save()
                #
                #         set_default_shipping = form.cleaned_data.get(
                #             'set_default_shipping')
                #         if set_default_shipping:
                #             shipping_address.default = True
                #             shipping_address.save()
                #
                #     else:
                #         messages.info(
                #             self.request, "Please fill in the required shipping address fields")
                #
                # use_default_billing = form.cleaned_data.get(
                #     'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    # billing_address.save()
                    # billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
                # elif use_default_billing:
                #     print("Using the defualt billing address")
                #     address_qs = Address.objects.filter(
                #         user=self.request.user,
                #         address_type='B',
                #         default=True
                #     )
                #     if address_qs.exists():
                #         billing_address = address_qs[0]
                #         order.billing_address = billing_address
                #         order.save()
                #     else:
                #         messages.info(
                #             self.request, "No default billing address available")
                #         return redirect('core:checkout')
                else:
                #     print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    # billing_country = form.cleaned_data.get(
                    #     'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')
                #
                #     if is_valid_form([billing_address1, billing_country, billing_zip]):
                #         billing_address = Address(
                #             user=self.request.user,
                #             street_address=billing_address1,
                #             apartment_address=billing_address2,
                #             country=billing_country,
                #             zip=billing_zip,
                #             address_type='B'
                #         )
                #         billing_address.save()
                #
                #         order.billing_address = billing_address
                #         order.save()
                #
                #         set_default_billing = form.cleaned_data.get(
                #             'set_default_billing')
                #         if set_default_billing:
                #             billing_address.default = True
                #             billing_address.save()
                #
                #     else:
                #         messages.info(
                #             self.request, "Please fill in the required billing address fields")

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
                return render(request, "tables/payment.html", context=context)
        except ObjectDoesNotExist:
            context = {
            'num_of_items': getCartSize(request),
            'note': "You do not have an active order"
            }
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

def getCartListByRestaurant(request):
    order_list = dict()
    customer_exists = Customer.objects.filter(user_id = request.user.id).exists()
    if customer_exists:
        customer = Customer.objects.get(user_id = request.user.id)
        order_qs = Order.objects.filter(customer_id=customer.id, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            order_list = order.get_total_by_restaurant()
    return order_list

def getTotal(request):
    order_total_price = 0.0
    customer_exists = Customer.objects.filter(user_id = request.user.id).exists()
    if customer_exists:
        customer = Customer.objects.get(user_id = request.user.id)
        order_qs = Order.objects.filter(customer_id=customer.id, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            order_total_price = order.get_total()
    return order_total_price

def join(request):
    return render(request, 'tables/join.html')
