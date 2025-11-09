from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ReservationForm
from django.conf import settings
import os
import urllib.request
import urllib.error
import json
import xml.etree.ElementTree as ET
from datetime import datetime


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
    form = ReservationForm()
    # Social feeds (opcionales, tolerantes a fallos)
    youtube_channel_id = getattr(settings, 'YOUTUBE_CHANNEL_ID', os.getenv('YOUTUBE_CHANNEL_ID', ''))
    instagram_username = getattr(settings, 'INSTAGRAM_USERNAME', os.getenv('INSTAGRAM_USERNAME', 'yosoyescalona'))

    youtube_videos = _fetch_youtube_videos(youtube_channel_id, limit=6)
    instagram_posts = _fetch_instagram_posts(instagram_username, limit=6)

    return render(request, 'reservas/home.html', {
        'form': form,
        'youtube_videos': youtube_videos,
        'instagram_posts': instagram_posts,
        'facebook_page_url': 'https://www.facebook.com/natursur',
        'youtube_channel_url': 'https://www.youtube.com/@natursur',
        'instagram_profile_url': 'https://www.instagram.com/yosoyescalona',
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
