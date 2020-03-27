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
    #path('', jobs.views.home, name='home'),
    #path('', customers.views.home, name='home'),
    path('', views.home, name='home'),
    path('Popeyes', views.Popeyes, name='Popeyes'),
    path('PapaPizzaPie', views.PapaPizzaPie, name='PapaPizzaPie'),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/signup', views.SignUp.as_view(), name='signup'),
    path('auth/customersignup', views.fillCustomer, name='fillCustomer'),
    path('auth/customersignup/address', views.fillAddress, name='fillAddress'),
    path('join', views.join, name='join'),
    #path('jobs/<int:job_id>', jobs.views.detail, name='detail'),
    # experimental paths for editing stuff
    path('auth/user-profile', views.profile, name='user-profile'),
    path('auth/user-profile/edit_customer', views.edit_customer, name='edit_customer'),
    path('auth/user-profile/address/<int:address_id>', views.edit_address, name='edit_address'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
