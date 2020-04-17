"""portfolio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from tables import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/signup', views.SignUp.as_view(), name='signup'),
    path('auth/customersignup', views.fillCustomer, name='fillCustomer'),
    path('auth/customersignup/address', views.fillAddress, name='fillAddress'),
    path('join', views.join, name='join'),
    path('auth/user-profile', views.profile, name='user-profile'),
    path('auth/user-profile/edit_customer', views.edit_customer, name='edit_customer'),
    path('auth/user-profile/address/<int:address_id>', views.edit_address, name='edit_address'),
    path('auth/user-profile/add-address/<int:customer_id>', views.add_address, name='add_address'),
    path('restaurant/<int:restaurant_id>', views.restaurantView, name='restaurantView'),
    path('auth/user-profile/delete/<int:address_id>', views.delete_address, name='delete_address'),
    path('auth/user-profile/edit_cuisine/<int:customer_id>', views.edit_cuisine, name='edit_cuisine'),
    path('dashboard', views.load_dashboard, name='load_dashboard'),
    path('cart', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('confirmation', views.confirmation, name='confirmation'),
    # new branch stuff below
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name="add_to_cart"),
    path('item/delete/<int:item_id>/', views.delete_from_cart, name="delete_item"),
    # url(r'^add-to-cart/(?P<item_id>[-\w]+)/$', add_to_cart, name="add_to_cart"),
    # url(r'^item/delete/(?P<item_id>[-\w]+)/$', delete_from_cart, name='delete_item'),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
