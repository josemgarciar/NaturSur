from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ReservationForm
from django.conf import settings
import os
import urllib.request
import urllib.error
import json
import xml.etree.ElementTree as ET
from datetime import datetime, date as ddate, time as dtime, timedelta
from .models import Reservation as ReservationModel

# Authentication imports
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import get_user_model


def _fetch_youtube_videos(channel_id: str, limit: int = 6):
    """
    Obtiene los últimos videos de YouTube usando el feed RSS público del canal.
    No requiere API key.

    Retorna lista de dicts: {title, url, image, published_at}
    """
    if not channel_id:
        return []
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        req = urllib.request.Request(feed_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            content = resp.read()
        # Parse RSS (Atom)
        root = ET.fromstring(content)
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'media': 'http://search.yahoo.com/mrss/',
            'yt': 'http://www.youtube.com/xml/schemas/2015'
        }
        entries = []
        for entry in root.findall('atom:entry', ns)[:limit]:
            title = (entry.find('atom:title', ns).text or '').strip()
            link = entry.find('atom:link', ns).attrib.get('href')
            published = entry.find('atom:published', ns).text
            video_id = entry.find('yt:videoId', ns).text if entry.find('yt:videoId', ns) is not None else None
            # Thumbnail estándar de YouTube por ID
            image = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else None
            entries.append({
                'title': title,
                'url': link,
                'image': image,
                'published_at': published,
            })
        return entries
    except Exception:
        return []


def _fetch_instagram_posts(username: str, limit: int = 6):
    """
    Obtiene últimas publicaciones públicas del usuario de Instagram.
    
    Instagram cambió su estructura a React, lo que hace que el scraping directo sea complejo.
    Como fallback, devolvemos un estado "sin conexión" que permite que la página funcione.
    Para producción, se recomienda usar Instagram Graph API con credenciales oficiales.
    
    Retorna lista de dicts: {caption, url, image, timestamp}
    """
    if not username:
        return []
    
    # Por ahora, retorna vacío (muestra el botón de enlace)
    # En futuro: implementar con Playwright/Selenium o usar Instagram Graph API oficial
    return []


def home(request):
    # If an offering id is provided in GET, preselect it in the form
    offering_prefill = request.GET.get('offering')
    if offering_prefill:
        form = ReservationForm(initial={'offering': offering_prefill})
    else:
        form = ReservationForm()
    # Social feeds (opcionales, tolerantes a fallos)
    youtube_channel_id = getattr(settings, 'YOUTUBE_CHANNEL_ID', os.getenv('YOUTUBE_CHANNEL_ID', ''))
    instagram_username = getattr(settings, 'INSTAGRAM_USERNAME', os.getenv('INSTAGRAM_USERNAME', 'yosoyescalona'))

    youtube_videos = _fetch_youtube_videos(youtube_channel_id, limit=6)
    instagram_posts = _fetch_instagram_posts(instagram_username, limit=6)
    from .models import Offering
    offerings = Offering.objects.all().order_by('duration_minutes')

    # Compute available times when offering and date are provided as GET params
    available_times = None
    offering_id = request.GET.get('offering')
    date_str = request.GET.get('date')
    if offering_id and date_str:
        try:
            offering_obj = Offering.objects.get(pk=offering_id)
            # parse date yyyy-mm-dd
            req_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            business_start = dtime(9, 0)
            business_end = dtime(18, 0)
            step = timedelta(minutes=30)
            duration = timedelta(minutes=(offering_obj.duration_minutes or 60))

            slots = []
            current_dt = datetime.combine(req_date, business_start)
            last_start_dt = datetime.combine(req_date, business_end) - duration

            # reservations on that date
            qs = ReservationModel.objects.filter(date=req_date)

            while current_dt <= last_start_dt:
                slot_end = current_dt + duration
                overlaps = False
                for r in qs:
                    r_start = datetime.combine(r.date, r.time)
                    r_end = r_start + timedelta(minutes=(r.offering.duration_minutes if r.offering else 60))
                    # overlap if start < r_end and r_start < end
                    if (current_dt < r_end) and (r_start < slot_end):
                        overlaps = True
                        break
                if not overlaps and current_dt >= datetime.combine(ddate.today(), dtime(0, 0)):
                    slots.append(current_dt.time().strftime('%H:%M'))
                current_dt = current_dt + step

            available_times = slots
        except Exception:
            available_times = None

    return render(request, 'reservas/home.html', {
        'form': form,
        'offerings': offerings,
        'youtube_videos': youtube_videos,
        'instagram_posts': instagram_posts,
        'facebook_page_url': 'https://www.facebook.com/natursur',
        'youtube_channel_url': 'https://www.youtube.com/@natursur',
        'instagram_profile_url': 'https://www.instagram.com/yosoyescalona',
        'available_times': available_times,
        'selected_date': date_str,
    })


def reservar(request):
    if request.method != 'POST':
        return redirect('home')
    # Quick-reserve button posts only 'offering' when user clicks price card
    if 'offering' in request.POST and not any(k in request.POST for k in ('name','email','phone')):
        # redirect to home with offering preselected (anchor to reservas)
        return redirect(f"{reverse('home')}?offering={request.POST.get('offering')}#reservas")

    form = ReservationForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect('reserva_exito')

    return render(request, 'reservas/home.html', {'form': form})


def reserva_exito(request):
    return render(request, 'reservas/booking_success.html')


def estudio_corporal(request):
    """Render simple informational page 'Estudio corporal'."""
    return render(request, 'reservas/estudio_corporal.html')


def mis_cinco_consejos(request):
    """Render 'Mis cinco consejos' informational page (reused hero from attachment).
    This page is internal and can be expanded later with contact form or application flow.
    """
    return render(request, 'reservas/mis_cinco_consejos.html')


def tienda(request):
    # Redirige directamente a la tienda externa para evitar embedding en iframe.
    return redirect(settings.EXTERNAL_SHOP_URL)


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # By default new users are not staff
            login(request, user)
            messages.success(request, 'Cuenta creada. Bienvenido, ahora puedes reservar.')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'reservas/signup.html', {'form': form})


@user_passes_test(lambda u: u.is_staff)
def admin_reservations(request):
    # View that shows all reservations to staff users
    from .models import Reservation
    qs = Reservation.objects.select_related('offering').order_by('-date', '-time')
    return render(request, 'reservas/admin_reservations.html', {'reservations': qs})


def logout_view(request):
    """Logout view that accepts GET and POST to simplify client-side logout links."""
    if request.method in ('POST', 'GET'):
        logout(request)
        messages.info(request, 'Has cerrado sesión.')
        return redirect('home')
    # method not allowed
    from django.http import HttpResponseNotAllowed
    return HttpResponseNotAllowed(['GET', 'POST'])
