from django.shortcuts import render, get_object_or_404, redirect
from .forms import CustomSignupForm
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
    success_url = reverse_lazy('customersignup')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        valid = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return valid

def customersignup(request):
    return render(request, 'registration/customer-registration.html')

def join(request):
    return render(request, 'tables/join.html')
