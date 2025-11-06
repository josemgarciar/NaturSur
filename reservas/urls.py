from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('reservar/', views.reservar, name='reservar'),
    path('reserva-exito/', views.reserva_exito, name='reserva_exito'),
    path('tienda/', views.tienda, name='tienda'),
]
