from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Customer, Address, Customer_Address, Cuisine
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

class CuisineForm(forms.Form):
    cuisines = forms.ModelMultipleChoiceField(queryset=Cuisine.objects.all(), widget=forms.CheckboxSelectMultiple)
# class CuisineForm(forms.Form):
#     cuisines = forms.ModelMultipleChoiceField(queryset=Cuisine.objects.all(), widget=Select2MultipleWidget)
