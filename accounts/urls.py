from os import stat
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/$', views.login_view, name='login'),
    path('', views.login_view, name='home'),
    path('register/', views.register_view, name = 'home'),
    path('logout/', views.logout_view, name='logout'),
]