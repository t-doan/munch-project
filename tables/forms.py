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

class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_state = forms.CharField(label='State', max_length=50)
    shipping_zip = forms.CharField(required=False)

    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_state = forms.CharField(label='State', max_length=50)
    billing_zip = forms.CharField(required=False)

    same_billing_address = forms.BooleanField(required=False)
    # set_default_shipping = forms.BooleanField(required=False)
    # use_default_shipping = forms.BooleanField(required=False)
    # set_default_billing = forms.BooleanField(required=False)
    # use_default_billing = forms.BooleanField(required=False)

    # payment_option = forms.ChoiceField(
    #     widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class BillingCheckout(forms.Form):
    billing_street = forms.CharField(label='Address', max_length=50)
    billing_city = forms.CharField(label='City', max_length=50)
    billing_state = forms.CharField(label='State', max_length=50)
    billing_zipcode = forms.CharField(label='Zipcode', max_length=15)

class DeliveryCheckout(forms.Form):
    delivery_street = forms.CharField(label='Address', max_length=50)
    delivery_city = forms.CharField(label='City', max_length=50)
    delivery_state = forms.CharField(label='State', max_length=50)
    delivery_zipcode = forms.CharField(label='Zipcode', max_length=15)
