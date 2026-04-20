"""
URL configuration for travelproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from . import views

urlpatterns = [
    path('404/',views.Page_404,name='404'),
    path('contact/',views.contact,name='contact'),
    path('testimonial/',views.testimonial,name='testimonial'),
    path('guides/',views.guides,name='guides'),
    path('gallery/',views.gallery,name='gallery'),
    path('booking/',views.booking,name='booking'),
    path('tour/',views.tour,name='tour'),
    path('index/',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('register/',views.register,name='register'),
    path('blog/',views.blog,name='blog'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('services/',views.services,name='services'),
    path('packages/',views.packages,name='packages'),
    path('destination/',views.destination,name='destination'),
    path('forget_password/',views.forget_password,name='forget_password'),
    path('update_password/',views.update_password,name='update_password'),
    path('otp/',views.otp,name='otp'),
    path('resetpassword/',views.resetpassword,name='resetpassword'),
    path('profile/',views.profile,name='profile'),
    path('add_tour/',views.add_tour,name='add_tour'),
    path('view_tour/',views.view_tour,name='view_tour'),
    path('edit_tour/<int:pk>/', views.edit_tour, name='edit_tour'),
    path('delete_tour/<int:pk>/',views.delete_tour,name='delete_tour'),
    path('update_tour/<int:pk>/',views.update_tour,name='update_tour'),
    
    
]
