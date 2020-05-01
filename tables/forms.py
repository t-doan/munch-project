from django import forms
from django.forms import Textarea, NumberInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Customer, Address, Customer_Address, Review
from django_select2.forms import Select2MultipleWidget
from datetime import date

CARD_TYPES = [
    ('','Card Type'),
    ('visa', 'Visa'),
    ('mastercard', 'Mastercard'),
    ('amex', 'American Express'),
    ('discover', 'Discover'),
    ('giftcard', 'Gift Card')
]

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
    shipping_address = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Street'}))
    shipping_city = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'City'}))
    shipping_state = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'State'}))
    shipping_zip = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Zipcode'}))

    billing_address = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Street'}))
    billing_city = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'City'}))
    billing_state = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'State'}))
    billing_zip = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Zipcode'}))

    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

<<<<<<< HEAD
class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)
=======
    # payment_option = forms.ChoiceField(
    #     widget=forms.RadioSelect, choices=PAYMENT_CHOICES)

# class PaymentForm(forms.Form):
#     card_type = forms.ChoiceField(
#         required=False,
#         widget=forms.CheckboxSelectMultiple,
#         choices=CARD_TYPES
#         attrs={'placeholder': 'Card Type'}
#     )
#     card_holder = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': "Card Holder's Name"}))
#     card_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Card Number'}))
#     experation = forms.DateField(label="Card's Experation Date", widget=forms.widgets.DateInput(format="%m/%Y"))
#     cvv = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "CVV"}))
>>>>>>> Tbranch
