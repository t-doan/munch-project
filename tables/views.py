from django.shortcuts import render, get_object_or_404, redirect
from .forms import CustomSignupForm, CustomerForm, AddressForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
import stripe
from decouple import config

from .models import Restaurant
from .models import Address, Customer, Customer_Address
from .models import Menu, Item

stripe.api_key = config('STRIPE_API_KEY')

# Create your views here.
def home(request):
    restaurants = Restaurant.objects
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
    'num_visits': num_visits,
    'restaurants':restaurants,
    }
    return render (request, 'tables/home.html',context = context)

def Popeyes(request):
    restaurant = Restaurant.objects.get(name = "Popeyes")
    menu = Menu.objects.get(restaurant_id_id = restaurant.id)
    item = Item.objects.get(menu_id_id = Menu.objects.get(restaurant_id_id = Restaurant.objects.get(name = "Popeyes").id).id) #multiple items, so might need a for loop
    return render(request, 'tables/Popeyes.html', {'restaurant':restaurant, 'menu':menu, 'item':item})

def PapaPizzaPie(request):
    return render(request, 'tables/PapaPizzaPie.html')

def restaurantView(request, restaurant_id):
    restaurant = Restaurant.objects.get(pk = restaurant_id)
    menu = Menu.objects.get(restaurant_id_id = restaurant.id)
    items = list(Item.objects.filter(menu_id=menu.id))
    return render(request, 'tables/restaurant_view.html', {'restaurant':restaurant, 'menu':menu, 'items':items})

def profile(request):
    customer = Customer.objects.get(user_id=request.user.id)
    customer_addresses = list(Customer_Address.objects.filter(customer_id_id=customer.id))
    addresses = []
    for cust_add in customer_addresses:
        addresses.append(Address.objects.get(id = cust_add.address_id_id))
    return render(request, 'registration/user-profile.html', {'customer':customer, 'addresses':addresses})

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
    print(request.user.id)
    form = CustomerForm(instance = customer)
    if request.method == 'POST':
        filled_form = CustomerForm(request.POST, instance=customer)
        if filled_form.is_valid():
            filled_form.save()
            form = filled_form
            note = 'Your info has been successfully changed'
        else:
            note = 'There was an error in changing your information'
        return render(request, 'registration/edit_customer.html', {'form':form, 'note':note})
    return render(request, 'registration/edit_customer.html', {'form':form})

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

def edit_address(request, address_id):
    address = Address.objects.get(pk=address_id)
    form = AddressForm(instance = address)
    if request.method == 'POST':
        filled_form = AddressForm(request.POST, instance=address)
        if filled_form.is_valid():
            filled_form.save()
            form = filled_form
            note = 'Your info has been successfully changed'
            return render(request, 'registration/edit_address.html', {'form':form, 'note':note, 'address':address})
    return render(request, 'registration/edit_address.html', {'form':form, 'address':address})

def join(request):
    return render(request, 'tables/join.html')
