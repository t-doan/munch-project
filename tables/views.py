from django.shortcuts import render, get_object_or_404, redirect
from .forms import CustomSignupForm, CustomerForm, AddressForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
import stripe
from decouple import config

from .models import Restaurant

stripe.api_key = config('STRIPE_API_KEY')

# Create your views here.
def home(request):
    restaurants = Restaurant.objects
    return render(request, 'tables/home.html', {'restaurants':restaurants})

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
    # if request.method == 'POST':
    #     filled_form = PizzaForm(request.POST)
    #     if filled_form.is_valid():
    #         created_pizza = filled_form.save()
    #         created_pizza_pk = created_pizza.id
    #         note = 'Thanks for ordering! Your %s %s and %s pizza is on its way!' %(filled_form.cleaned_data['size'],
    #         filled_form.cleaned_data['topping1'],
    #         filled_form.cleaned_data['topping2'],)
    #         filled_form = PizzaForm()
    #     else:
    #         created_pizza_pk = None
    #         note = 'Order was not created, please try again'
    #     return render(request, 'pizza/order.html', {'created_pizza_pk':created_pizza_pk, 'pizzaform':filled_form, 'note':note, 'multiple_form':multiple_form})
    # else:
        customer_form = CustomerForm()
        return render(request, 'registration/customer-registration.html', {'form':customer_form})

def fillAddress(request):
    # if request.method == 'POST':
    #     filled_form = PizzaForm(request.POST)
    #     if filled_form.is_valid():
    #         created_pizza = filled_form.save()
    #         created_pizza_pk = created_pizza.id
    #         note = 'Thanks for ordering! Your %s %s and %s pizza is on its way!' %(filled_form.cleaned_data['size'],
    #         filled_form.cleaned_data['topping1'],
    #         filled_form.cleaned_data['topping2'],)
    #         filled_form = PizzaForm()
    #     else:
    #         created_pizza_pk = None
    #         note = 'Order was not created, please try again'
    #     return render(request, 'pizza/order.html', {'created_pizza_pk':created_pizza_pk, 'pizzaform':filled_form, 'note':note, 'multiple_form':multiple_form})
    # else:
        address_form = AddressForm()
        return render(request, 'registration/address.html', {'form':address_form})

def join(request):
    return render(request, 'tables/join.html')
