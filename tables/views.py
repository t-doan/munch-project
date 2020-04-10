from django.shortcuts import render, get_object_or_404, redirect
from .forms import CustomSignupForm, CustomerForm, AddressForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
import stripe
import googlemaps
from decouple import config

from .models import Restaurant, Menu, Item, Cuisine, Customer_Cuisine
from .models import Address, Customer, Customer_Address, Restaurant_Cuisine

stripe.api_key = config('STRIPE_API_KEY')
gmaps = googlemaps.Client(key=config('GOOGLE_API_KEY'))

# Create your views here.
def home(request):
    # TEST CODE FOR GOOGLE MAPS API
    my_dist = gmaps.distance_matrix('1331 E Louisa Ave, West Covina', '521 Timberline Dr, Azusa', units='imperial')['rows'][0]['elements'][0]
    print(my_dist)
    print(type(my_dist))
    # dist_dict = my_dist['distance']
    dist_text = my_dist['distance']['text']
    print(dist_text)
    ####
    restaurants = Restaurant.objects
    # num_visits = request.session.get('num_visits', 0)
    # request.session['num_visits'] = num_visits + 1

    context = {
    # 'num_visits': num_visits,
    'restaurants':restaurants,
    }
    return render (request, 'tables/home.html',context = context)

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
    context = {
    'restaurant':restaurant,
    'menu_names':menu_names,
    'menu_items':menu_items,
    'i_amt':range(len(menu_names)),
    'cuisines_str':cuisines_str
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
        print(request.POST)
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

def join(request):
    return render(request, 'tables/join.html')
