from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('reservar/', views.reservar, name='reservar'),
    path('reserva-exito/', views.reserva_exito, name='reserva_exito'),
    path('tienda/', views.tienda, name='tienda'),
    # Auth
    path('accounts/signup/', views.signup_view, name='signup'),
    path('accounts/login/', views.LoginView.as_view(template_name='reservas/login.html'), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    # Admin reservations overview
    path('admin/reservas/', views.admin_reservations, name='admin_reservations'),
]
