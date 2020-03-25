from django.shortcuts import render, get_object_or_404, redirect
from .forms import CustomSignupForm, CustomerForm, AddressForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
import stripe
from decouple import config

from .models import Restaurant
from .models import Address, Customer

stripe.api_key = config('STRIPE_API_KEY')

# Create your views here.
def home(request):
    restaurants = Restaurant.objects
    return render(request, 'tables/home.html', {'restaurants':restaurants})

def profile(request):
    return render(request, 'registration/user-profile.html')

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
            # created_customer_pk = created_customer.id
            address_form = AddressForm()
            return render(request, 'registration/address.html', {'form':address_form,})
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
    # if request.method == 'POST':
        filled_form = AddressForm(request.POST)
        # print ("Address post")
        if filled_form.is_valid():
            created_address = filled_form.save()
            created_address_pk = created_address.id
        #    note = 'Address Saved!'
            # print ('Address saved')
            filled_form = AddressForm()
        else:
            created_address_pk = None
        #    note = 'Order was not created, please try again'
            # print ('Not valid form')
        return render(request, 'tables/home.html', {'created_address_pk':created_address_pk})
    # else:
    #     print ("Address get")
    #     address_form = AddressForm()
    #     return render(request, 'registration/address.html', {'form':address_form})

def edit_address(request, pk):
    address = Address.objects.get(pk=pk)
    form = AddressForm(instance = address)
    if request.method == 'POST':
        filled_form = AddressForm(request.POST, instance=address)
        if filled_form.is_valid():
            filled_form.save()
            form = filled_form
            note = 'Your info has been successfully changed'
    return render(request, 'registration/edit_customer.html', {'form':customer_form, 'note':note, })

def join(request):
    return render(request, 'tables/join.html')
