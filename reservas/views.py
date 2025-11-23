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
from django.http import JsonResponse

# Authentication imports
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


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
    # Prepare initial values for the reservation form
    initial = {}
    if offering_prefill:
        initial['offering'] = offering_prefill
    # If user is authenticated, prefill name and email when available
    if request.user.is_authenticated:
        full_name = (getattr(request.user, 'first_name', '') + ' ' + getattr(request.user, 'last_name', '')).strip()
        initial['name'] = full_name if full_name else getattr(request.user, 'username', '')
        if getattr(request.user, 'email', ''):
            initial['email'] = request.user.email

    form = ReservationForm(initial=initial) if initial else ReservationForm()
    # Prevent selecting past dates in the date picker: set min to today (YYYY-MM-DD)
    try:
        today_str = ddate.today().isoformat()
        if 'date' in form.fields:
            form.fields['date'].widget.attrs['min'] = today_str
    except Exception:
        pass
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
    # Also prepare a full list of slots for UI when no date is selected
    all_slots = []
    try:
        business_start = dtime(9, 0)
        business_end = dtime(18, 0)
        step = timedelta(minutes=30)
        current_dt = datetime.combine(ddate.today(), business_start)
        last_start_dt = datetime.combine(ddate.today(), business_end) - step
        while current_dt <= last_start_dt:
            all_slots.append(current_dt.time().strftime('%H:%M'))
            current_dt = current_dt + step
    except Exception:
        all_slots = []
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
        'all_slots': all_slots,
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
        reservation = form.save()
        # Send confirmation email
        _send_confirmation_email(reservation)
        return redirect('reserva_exito')

    return render(request, 'reservas/home.html', {'form': form})


def reserva_exito(request):
    return render(request, 'reservas/booking_success.html')


def estudio_corporal(request):
    """Render simple informational page 'Estudio corporal'."""
    return render(request, 'reservas/estudio_corporal.html')


def unete_al_equipo(request):
    """Render 'Únete al equipo' informational page (reused hero from attachment).
    This page is internal and can be expanded later with contact form or application flow.
    """
    return render(request, 'reservas/unete_al_equipo.html')

def available_times_api(request):
    """Return JSON list of available time strings (HH:MM) for a given offering and date.
    GET params: offering (id), date (YYYY-MM-DD)
    """
    offering_id = request.GET.get('offering')
    date_str = request.GET.get('date')
    if not offering_id or not date_str:
        return JsonResponse({'times': []})
    try:
        from .models import Offering
        offering_obj = Offering.objects.get(pk=offering_id)
        req_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        business_start = dtime(9, 0)
        business_end = dtime(18, 0)
        step = timedelta(minutes=30)
        duration = timedelta(minutes=(offering_obj.duration_minutes or 60))

        slots = []
        current_dt = datetime.combine(req_date, business_start)
        last_start_dt = datetime.combine(req_date, business_end) - duration

        qs = ReservationModel.objects.filter(date=req_date)

        while current_dt <= last_start_dt:
            slot_end = current_dt + duration
            overlaps = False
            for r in qs:
                r_start = datetime.combine(r.date, r.time)
                r_end = r_start + timedelta(minutes=(r.offering.duration_minutes if r.offering else 60))
                if (current_dt < r_end) and (r_start < slot_end):
                    overlaps = True
                    break
            if not overlaps and current_dt >= datetime.combine(ddate.today(), dtime(0, 0)):
                slots.append(current_dt.time().strftime('%H:%M'))
            current_dt = current_dt + step

        return JsonResponse({'times': slots})
    except Exception:
        return JsonResponse({'times': []})


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


@user_passes_test(lambda u: u.is_staff)
def admin_clients(request):
    # View that shows all registered users (clients)
    User = get_user_model()
    # Get all non-staff users (regular clients), ordered by date joined
    clients = User.objects.filter(is_staff=False).order_by('-date_joined')
    return render(request, 'reservas/admin_clients.html', {'clients': clients})


@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    # Admin dashboard with overview
    from .models import Reservation
    User = get_user_model()
    reservations_count = Reservation.objects.count()
    clients_count = User.objects.filter(is_staff=False).count()
    context = {
        'reservations_count': reservations_count,
        'clients_count': clients_count,
    }
    return render(request, 'reservas/admin_dashboard.html', context)


def _send_confirmation_email(reservation):
    """Send a confirmation email for a reservation using Resend.com API with HTML formatting."""
    try:
        if not reservation.email:
            logger.warning('Reservation %s has no email address', reservation.id)
            return
        
        # Build email content
        subject = f"Confirmación de reserva - {reservation.offering.name if reservation.offering else 'Natursur'}"
        date_str = reservation.date.strftime('%d/%m/%Y') if reservation.date else ''
        time_str = reservation.time.strftime('%H:%M') if reservation.time else ''
        duration = f"{reservation.offering.duration_minutes} minutos" if reservation.offering and reservation.offering.duration_minutes else ''
        price = f"€{reservation.offering.price_eur}" if reservation.offering and hasattr(reservation.offering, 'price_eur') else ''
        
        # Plain text version
        text_message = (
            f"Hola {reservation.name},\n\n"
            f"¡Gracias por reservar con Natursur! Aquí tienes los detalles de tu cita:\n\n"
            f"Servicio: {reservation.offering.name if reservation.offering else 'No especificado'}\n"
            f"Fecha: {date_str}\n"
            f"Hora: {time_str}\n"
            f"Duración: {duration}\n"
            f"Precio: {price}\n\n"
            f"Teléfono: {reservation.phone if reservation.phone else 'No proporcionado'}\n\n"
            f"Si necesitas cambiar o cancelar tu reserva, no dudes en contactarnos.\n\n"
            f"¡Te esperamos!\n"
            f"Natursur"
        )
        
        # HTML version with styling
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
                .details {{ background: white; padding: 20px; border-radius: 6px; margin: 20px 0; }}
                .detail-row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee; }}
                .detail-row:last-child {{ border-bottom: none; }}
                .detail-label {{ font-weight: 600; color: #2d5016; }}
                .detail-value {{ color: #666; }}
                .price-highlight {{ background: #2d5016; color: white; padding: 15px; border-radius: 6px; font-size: 24px; font-weight: bold; text-align: center; margin: 15px 0; }}
                .footer {{ background: #2d5016; color: white; padding: 20px; border-radius: 0 0 8px 8px; text-align: center; font-size: 12px; }}
                .cta {{ background: #4a7c2c; color: white; padding: 12px 30px; border-radius: 6px; text-decoration: none; display: inline-block; margin-top: 15px; }}
                .warning {{ background: #fff3cd; color: #856404; padding: 12px; border-radius: 4px; margin-top: 20px; font-size: 13px; border-left: 4px solid #ffc107; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✓ Reserva Confirmada</h1>
                    <p style="margin: 10px 0 0 0;">Tu cita en Natursur</p>
                </div>
                
                <div class="content">
                    <p style="font-size: 16px; margin-top: 0;">Hola <strong>{reservation.name}</strong>,</p>
                    
                    <p>¡Gracias por reservar con Natursur! Tu reserva ha sido confirmada. Aquí tienes los detalles de tu cita:</p>
                    
                    <div class="details">
                        <div class="detail-row">
                            <span class="detail-label">📋 Servicio:</span>
                            <span class="detail-value">{reservation.offering.name if reservation.offering else 'No especificado'}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">📅 Fecha:</span>
                            <span class="detail-value">{date_str}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">🕐 Hora:</span>
                            <span class="detail-value">{time_str}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">⏱️ Duración:</span>
                            <span class="detail-value">{duration}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">☎️ Contacto:</span>
                            <span class="detail-value">{reservation.phone if reservation.phone else 'No proporcionado'}</span>
                        </div>
                    </div>
                    
                    <div class="price-highlight">{price}</div>
                    
                    <p style="color: #666; font-size: 14px;">Si necesitas cambiar o cancelar tu reserva, no dudes en contactarnos respondiendo a este email o llamándonos.</p>
                    
                    <div class="warning">
                        <strong>💡 Recordatorio:</strong> Por favor, intenta llegar 5-10 minutos antes de tu cita.
                    </div>
                </div>
                
                <div class="footer">
                    <p style="margin: 0; font-weight: bold; margin-bottom: 8px;">Natursur</p>
                    <p style="margin: 0;">Cuidado, nutrición y experiencias relajantes con esencia del Sur</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        from_email = settings.DEFAULT_FROM_EMAIL
        
        # Always try Resend API if key is available
        if settings.RESEND_API_KEY:
            try:
                import resend
                resend.api_key = settings.RESEND_API_KEY
                logger.info('📧 Attempting to send HTML email via Resend to %s from %s', reservation.email, from_email)
                
                response = resend.Emails.send({
                    "from": from_email,
                    "to": reservation.email,
                    "subject": subject,
                    "html": html_message,
                    "text": text_message,
                })
                
                logger.info('📧 Resend response: %s', response)
                
                if isinstance(response, dict) and response.get('id'):
                    logger.info('✅ Confirmation email sent via Resend (ID: %s) to %s', response.get('id'), reservation.email)
                elif hasattr(response, 'id'):
                    logger.info('✅ Confirmation email sent via Resend (ID: %s) to %s', response.id, reservation.email)
                else:
                    logger.warning('⚠️ Resend response unexpected format: %s', response)
                return
            except Exception as resend_error:
                logger.error('❌ Failed to send email via Resend: %s. Error type: %s', str(resend_error), type(resend_error).__name__)
                # In DEBUG mode, still print to console; in production, this is the error we need to investigate
                if not settings.DEBUG:
                    raise  # Re-raise to stop execution in production
    except Exception as e:
        logger.exception('❌ Failed to send confirmation email for reservation %s: %s', getattr(reservation, 'id', 'unknown'), str(e))


def logout_view(request):
    """Logout view that accepts GET and POST to simplify client-side logout links."""
    if request.method in ('POST', 'GET'):
        logout(request)
        messages.info(request, 'Has cerrado sesión.')
        return redirect('home')
    # method not allowed
    from django.http import HttpResponseNotAllowed
    return HttpResponseNotAllowed(['GET', 'POST'])


@user_passes_test(lambda u: u.is_staff)
def delete_reservation(request, reservation_id):
    """Delete a reservation (admin only)."""
    from .models import Reservation
    reservation = Reservation.objects.get(id=reservation_id)
    
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, f'Reserva de {reservation.name} del {reservation.date} cancelada.')
        return redirect('admin_reservations')
    
    # GET - show confirmation page
    return render(request, 'reservas/confirm_delete_reservation.html', {'reservation': reservation})


@user_passes_test(lambda u: u.is_staff)
def delete_user(request, user_id):
    """Delete a user (admin only)."""
    User = get_user_model()
    user_to_delete = User.objects.get(id=user_id)
    
    # Prevent admin from deleting themselves or other admins
    if user_to_delete.is_staff or user_to_delete == request.user:
        messages.error(request, 'No puedes eliminar este usuario.')
        return redirect('admin_clients')
    
    if request.method == 'POST':
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f'Usuario "{username}" eliminado.')
        return redirect('admin_clients')
    
    # GET - show confirmation page
    return render(request, 'reservas/confirm_delete_user.html', {'user_to_delete': user_to_delete})


class CustomLoginView(LoginView):
    """Custom login view that redirects staff/admin users to admin panel."""
    template_name = 'reservas/login.html'
    
    def get_success_url(self):
        return reverse('home')


def contacto(request):
    """Contact page with WhatsApp link, Google Maps embed, and contact form."""
    context = {}
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Validate form
        if not all([name, email, subject, message]):
            messages.error(request, 'Por favor completa todos los campos obligatorios.')
            return redirect('contacto')
        
        # Send email to site admin
        try:
            admin_email = settings.DEFAULT_FROM_EMAIL or 'admin@natursur.com'
            from_email = settings.DEFAULT_FROM_EMAIL
            
            # Build email content
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
                    .header h1 {{ margin: 0; font-size: 28px; }}
                    .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
                    .details {{ background: white; padding: 20px; border-radius: 6px; margin: 20px 0; }}
                    .detail-row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee; }}
                    .detail-row:last-child {{ border-bottom: none; }}
                    .detail-label {{ font-weight: 600; color: #2d5016; }}
                    .detail-value {{ color: #666; word-break: break-word; }}
                    .message-box {{ background: #f0f0f0; padding: 15px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #4a7c2c; }}
                    .footer {{ background: #2d5016; color: white; padding: 20px; border-radius: 0 0 8px 8px; text-align: center; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📬 Nuevo Mensaje de Contacto</h1>
                    </div>
                    
                    <div class="content">
                        <p><strong>Asunto:</strong> {subject}</p>
                        
                        <div class="details">
                            <div class="detail-row">
                                <span class="detail-label">👤 Nombre:</span>
                                <span class="detail-value">{name}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">📧 Email:</span>
                                <span class="detail-value"><a href="mailto:{email}">{email}</a></span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">☎️ Teléfono:</span>
                                <span class="detail-value">{phone if phone else 'No proporcionado'}</span>
                            </div>
                        </div>
                        
                        <p><strong>Mensaje:</strong></p>
                        <div class="message-box">
                            {message.replace(chr(10), '<br>')}
                        </div>
                        
                        <p style="color: #666; font-size: 13px; margin-top: 20px;">
                            <strong>Responde a este email para contactar directamente con {name}.</strong>
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p style="margin: 0;">Natursur - Panel de Contacto</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_message = f"""
Nuevo mensaje de contacto

Asunto: {subject}
Nombre: {name}
Email: {email}
Teléfono: {phone if phone else 'No proporcionado'}

Mensaje:
{message}

Responde a este email para contactar directamente con {name}.
            """
            
            # Send via Resend API if available
            if settings.RESEND_API_KEY:
                try:
                    import resend
                    resend.api_key = settings.RESEND_API_KEY
                    logger.info('📧 Sending contact form email via Resend from %s to %s', from_email, admin_email)
                    
                    response = resend.Emails.send({
                        "from": from_email,
                        "to": admin_email,
                        "reply_to": email,  # Allow admin to reply directly to the user
                        "subject": f'[CONTACTO] {subject} - De: {name}',
                        "html": html_message,
                        "text": text_message,
                    })
                    
                    logger.info('📧 Resend response: %s', response)
                    
                    if isinstance(response, dict) and response.get('id'):
                        logger.info('✅ Contact form email sent via Resend (ID: %s) to %s', response.get('id'), admin_email)
                    elif hasattr(response, 'id'):
                        logger.info('✅ Contact form email sent via Resend (ID: %s) to %s', response.id, admin_email)
                    
                    context['success_message'] = True
                    messages.success(request, 'Mensaje enviado correctamente. Te responderemos pronto.')
                    return render(request, 'reservas/contacto.html', context)
                except Exception as resend_error:
                    logger.error('❌ Failed to send contact email via Resend: %s', str(resend_error))
                    if settings.DEBUG:
                        messages.warning(request, f'Aviso: {str(resend_error)}')
                    else:
                        messages.error(request, 'Error al enviar el mensaje. Por favor, intenta de nuevo.')
                        return redirect('contacto')
            else:
                # Fallback to Django's send_mail if Resend is not configured
                try:
                    send_mail(
                        subject=f'[CONTACTO] {subject} - De: {name}',
                        message=text_message,
                        from_email=from_email,
                        recipient_list=[admin_email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    context['success_message'] = True
                    messages.success(request, 'Mensaje enviado correctamente. Te responderemos pronto.')
                    logger.info('✅ Contact form email sent via Django mail to %s', admin_email)
                except Exception as e:
                    logger.error('❌ Error sending contact email: %s', str(e))
                    messages.error(request, 'Error al enviar el mensaje. Intenta de nuevo más tarde.')
                    return redirect('contacto')
        
        except Exception as e:
            logger.exception('❌ Unexpected error in contact form: %s', str(e))
            messages.error(request, 'Error inesperado. Por favor, intenta de nuevo.')
            return redirect('contacto')
    
    return render(request, 'reservas/contacto.html', context)


def faq(request):
    """FAQ page with collapsible questions and answers."""
    return render(request, 'reservas/faq.html')

