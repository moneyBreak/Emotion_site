from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from api import views

urlpatterns = [
    url('register', views.register),
    url('login', views.login),
]