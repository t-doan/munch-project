from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Customer, Address, Customer_Address
from django_select2.forms import Select2MultipleWidget

class CustomSignupForm(UserCreationForm):
    email = forms.EmailField(max_length=255, required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'phone_number')

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('nickname','street', 'city', 'state', 'zipcode',)

class OrderInfoForm(forms.Form):
    # Name
    first_name = forms.CharField(label='First Name', max_length=15)
    last_name = forms.CharField(label='Last Name', max_length=15)
    # Billing Address
    billing_street = forms.CharField(max_length=50)
    billing_city = forms.CharField(max_length=50)
    billing_state = forms.CharField(max_length=50)
    billing_zipcode = forms.CharField(max_length=15)
    # Order / Delivery Address
    delivery_street = forms.CharField(max_length=50)
    delivery_city = forms.CharField(max_length=50)
    delivery_state = forms.CharField(max_length=50)
    delivery_zipcode = forms.CharField(max_length=15)
