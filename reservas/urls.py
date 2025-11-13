from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('reservar/', views.reservar, name='reservar'),
    path('reserva-exito/', views.reserva_exito, name='reserva_exito'),
    path('tienda/', views.tienda, name='tienda'),
    path('estudio-corporal/', views.estudio_corporal, name='estudio_corporal'),
    path('mis-cinco-consejos/', views.mis_cinco_consejos, name='mis_cinco_consejos'),
    # Auth
    path('accounts/signup/', views.signup_view, name='signup'),
    path('accounts/login/', views.LoginView.as_view(template_name='reservas/login.html'), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    # Admin reservations overview
    path('admin/reservas/', views.admin_reservations, name='admin_reservations'),
]
