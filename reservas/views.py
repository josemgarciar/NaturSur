from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ReservationForm
from django.conf import settings


def home(request):
    form = ReservationForm()
    return render(request, 'reservas/home.html', {
        'form': form,
    })


def reservar(request):
    if request.method != 'POST':
        return redirect('home')

    form = ReservationForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect('reserva_exito')

    return render(request, 'reservas/home.html', {'form': form})


def reserva_exito(request):
    return render(request, 'reservas/booking_success.html')


def tienda(request):
    # Intenta embeber la tienda externa dentro de un iframe.
    # Nota: si el dominio remoto bloquea el embedding (X-Frame-Options/CSP),
    # mostraremos un fallback con enlace directo.
    return render(request, 'reservas/tienda.html', {
        'shop_url': settings.EXTERNAL_SHOP_URL,
    })
