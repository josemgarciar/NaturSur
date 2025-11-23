from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('reservar/', views.reservar, name='reservar'),
    path('reserva-exito/', views.reserva_exito, name='reserva_exito'),
    path('tienda/', views.tienda, name='tienda'),
    path('estudio-corporal/', views.estudio_corporal, name='estudio_corporal'),
    path('contacto/', views.contacto, name='contacto'),
    path('faq/', views.faq, name='faq'),
    path('unete-al-equipo/', views.unete_al_equipo, name='unete_al_equipo'),
    # API for async available times
    path('api/available-times/', views.available_times_api, name='available_times_api'),
    # Auth
    path('accounts/signup/', views.signup_view, name='signup'),
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    # Admin panel (personalized admin, not Django admin)
    path('panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/reservas/', views.admin_reservations, name='admin_reservations'),
    path('panel/clientes/', views.admin_clients, name='admin_clients'),
    # Admin actions (delete/cancel)
    path('panel/reservas/<int:reservation_id>/eliminar/', views.delete_reservation, name='delete_reservation'),
    path('panel/clientes/<int:user_id>/eliminar/', views.delete_user, name='delete_user'),
]
