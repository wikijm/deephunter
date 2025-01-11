from django.urls import path
from . import views

urlpatterns = [
    path('vthashchecker', views.vthashchecker, name='vthashchecker'),
    path('loldriverhashchecker', views.loldriverhashchecker, name='loldriverhashchecker'),
    path('whois', views.whois, name='whois'),
]
