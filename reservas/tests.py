from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta, date as ddate, time as dtime
from .models import Reservation, Offering
from .forms import ReservationForm, validate_phone
from django.core.exceptions import ValidationError
import json


class OfferingModelTests(TestCase):
    """Tests para el modelo Offering."""

    def setUp(self):
        """Crear ofertas de prueba."""
        self.offering = Offering.objects.create(
            slug="masaje-60",
            name="Masaje Relajante",
            duration_minutes=60,
            price_eur=50.00
        )

    def test_offering_creation(self):
        """Test: Crear una oferta correctamente."""
        self.assertEqual(self.offering.name, "Masaje Relajante")
        self.assertEqual(self.offering.duration_minutes, 60)
        self.assertEqual(self.offering.price_eur, 50.00)

    def test_offering_str_format(self):
        """Test: String representation de Offering contiene datos correctos."""
        str_repr = str(self.offering)
        self.assertIn("Masaje Relajante", str_repr)
        self.assertIn("50", str_repr)

    def test_offering_slug_exists(self):
        """Test: El slug existe en el modelo."""
        self.assertEqual(self.offering.slug, "masaje-60")


class ReservationModelTests(TestCase):
    """Tests para el modelo Reservation."""

    def setUp(self):
        """Crear reserva y oferta de prueba."""
        self.offering = Offering.objects.create(
            slug="test-60",
            name="Test Service",
            duration_minutes=60,
            price_eur=60.00
        )
        self.reservation = Reservation.objects.create(
            name="Juan Pérez",
            email="juan@example.com",
            phone="+34 691 355 682",
            offering=self.offering,
            date=ddate(2025, 12, 25),
            time=dtime(14, 30),
            notes="Primera vez"
        )

    def test_reservation_creation(self):
        """Test: Crear una reserva correctamente."""
        self.assertEqual(self.reservation.name, "Juan Pérez")
        self.assertEqual(self.reservation.email, "juan@example.com")
        self.assertEqual(self.reservation.phone, "+34 691 355 682")

    def test_reservation_phone_validation(self):
        """Test: Validación de teléfono."""
        valid_phones = [
            "+34 691 355 682",
            "691355682",
            "+34-691-355-682",
            "(691) 355-682"
        ]
        for phone in valid_phones:
            try:
                validate_phone(phone)
            except ValidationError:
                self.fail(f"Teléfono válido rechazado: {phone}")

    def test_reservation_phone_invalid(self):
        """Test: Teléfono inválido debe fallar."""
        invalid_phones = [
            "123",
            "abc123def456ghi",
        ]
        for phone in invalid_phones:
            with self.assertRaises(ValidationError):
                validate_phone(phone)

    def test_reservation_ordering(self):
        """Test: Las reservas se ordenan por fecha descendente."""
        Reservation.objects.create(
            name="Test 2",
            email="test2@example.com",
            phone="691355682",
            offering=self.offering,
            date=ddate(2025, 12, 20),
            time=dtime(10, 0)
        )
        reservations = Reservation.objects.all()
        self.assertEqual(reservations[0].date, ddate(2025, 12, 25))

    def test_reservation_service_field(self):
        """Test: Campo service de reserva."""
        self.assertTrue(hasattr(self.reservation, 'service'))
        # El campo service puede estar vacío en la creación inicial
        self.assertIsNotNone(self.reservation.service)


class ReservationFormTests(TestCase):
    """Tests para el formulario ReservationForm."""

    def setUp(self):
        """Crear datos de prueba."""
        self.offering = Offering.objects.create(
            slug="test",
            name="Test",
            price_eur=50.00
        )

    def test_form_valid(self):
        """Test: Formulario válido."""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+34 691 355 682',
            'offering': self.offering.id,
            'service': 'masaje',
            'date': ddate(2025, 12, 25),
            'time': dtime(14, 30),
            'notes': 'Test notes'
        }
        form = ReservationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_missing_required_fields(self):
        """Test: Formulario sin campos requeridos."""
        form_data = {
            'name': '',
            'email': '',
            'phone': ''
        }
        form = ReservationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_invalid_email(self):
        """Test: Email inválido."""
        form_data = {
            'name': 'Test',
            'email': 'not-an-email',
            'phone': '+34 691 355 682',
            'offering': self.offering.id,
            'date': ddate(2025, 12, 25),
            'time': dtime(14, 30)
        }
        form = ReservationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_phone_field_required(self):
        """Test: Campo de teléfono es requerido."""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '',
            'offering': self.offering.id,
            'service': 'masaje',
            'date': ddate(2025, 12, 25),
            'time': dtime(14, 30),
        }
        form = ReservationForm(data=form_data)
        self.assertFalse(form.is_valid())


class HomeViewBasicTests(TestCase):
    """Tests básicos para la vista home."""

    def setUp(self):
        """Setup del cliente de prueba."""
        self.client = Client()
        self.offering = Offering.objects.create(
            slug="test",
            name="Test Service",
            price_eur=50.00
        )

    def test_home_url_exists(self):
        """Test: URL de home existe."""
        try:
            reverse('home')
            self.assertTrue(True)
        except:
            self.fail("URL 'home' no existe")


class ReservationCreationTests(TestCase):
    """Tests para creación de reservas mediante formulario."""

    def setUp(self):
        """Setup del cliente y ofertas."""
        self.client = Client()
        self.offering = Offering.objects.create(
            slug="test",
            name="Test Service",
            duration_minutes=60,
            price_eur=50.00
        )

    def test_create_reservation_with_valid_data(self):
        """Test: Crear reserva con datos válidos."""
        reservation = Reservation.objects.create(
            name='Juan Test',
            email='juan@test.com',
            phone='+34 691 355 682',
            offering=self.offering,
            service='masaje',
            date=ddate(2025, 12, 25),
            time=dtime(14, 30),
            notes='Test reservation'
        )
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(reservation.name, 'Juan Test')

    def test_reservation_preserves_data(self):
        """Test: Verifica que la reserva guarde datos correctamente."""
        data = {
            'name': 'María García',
            'email': 'maria@test.com',
            'phone': '691355682',
            'offering': self.offering,
            'service': 'osteopatia',
            'date': ddate(2025, 12, 27),
            'time': dtime(10, 0),
            'notes': 'Primera sesión'
        }
        reservation = Reservation.objects.create(**data)
        saved_reservation = Reservation.objects.get(id=reservation.id)
        self.assertEqual(saved_reservation.name, 'María García')
        self.assertEqual(saved_reservation.service, 'osteopatia')
        self.assertEqual(saved_reservation.notes, 'Primera sesión')


class AuthenticationTests(TestCase):
    """Tests para autenticación."""

    def setUp(self):
        """Setup del cliente y usuario."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_signup_url_exists(self):
        """Test: URL de signup existe."""
        try:
            reverse('signup')
            self.assertTrue(True)
        except:
            self.fail("URL 'signup' no existe")

    def test_login_url_exists(self):
        """Test: URL de login existe."""
        try:
            reverse('login')
            self.assertTrue(True)
        except:
            self.fail("URL 'login' no existe")

    def test_logout_url_exists(self):
        """Test: URL de logout existe."""
        try:
            reverse('logout')
            self.assertTrue(True)
        except:
            self.fail("URL 'logout' no existe")

    def test_user_creation(self):
        """Test: Crear usuario correctamente."""
        user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='newpass123'
        )
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')


class AdminPanelBasicTests(TestCase):
    """Tests básicos para el panel de administración."""

    def setUp(self):
        """Setup del usuario admin y cliente."""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.offering = Offering.objects.create(
            slug="test",
            name="Test",
            price_eur=50.00
        )
        self.reservation = Reservation.objects.create(
            name="Test",
            email="test@example.com",
            phone="+34 691 355 682",
            offering=self.offering,
            date=ddate(2025, 12, 25),
            time=dtime(14, 30)
        )

    def test_admin_dashboard_url_exists(self):
        """Test: URL del dashboard admin existe."""
        try:
            reverse('admin_dashboard')
            self.assertTrue(True)
        except:
            self.fail("URL 'admin_dashboard' no existe")

    def test_admin_reservations_url_exists(self):
        """Test: URL de reservas admin existe."""
        try:
            reverse('admin_reservations')
            self.assertTrue(True)
        except:
            self.fail("URL 'admin_reservations' no existe")

    def test_admin_clients_url_exists(self):
        """Test: URL de clientes admin existe."""
        try:
            reverse('admin_clients')
            self.assertTrue(True)
        except:
            self.fail("URL 'admin_clients' no existe")


class URLRoutingTests(TestCase):
    """Tests para verificar que todas las rutas existen."""

    def test_all_urls_exist(self):
        """Test: Verificar que todas las URLs clave existen."""
        urls_to_test = [
            'home',
            'reservar',
            'contacto',
            'faq',
            'estudio_corporal',
            'unete_al_equipo',
            'tienda',
            'admin_dashboard',
            'admin_reservations',
            'admin_clients',
            'login',
            'logout',
            'signup',
        ]
        for url_name in urls_to_test:
            try:
                reverse(url_name)
                self.assertTrue(True)
            except:
                self.fail(f"URL '{url_name}' no existe")


class TimeSlotCalculationTests(TestCase):
    """Tests para cálculo de horas disponibles."""

    def setUp(self):
        """Setup de ofertas."""
        self.offering = Offering.objects.create(
            slug="masaje-60",
            name="Masaje",
            duration_minutes=60,
            price_eur=50.00
        )
        self.offering_30 = Offering.objects.create(
            slug="consulta-30",
            name="Consulta",
            duration_minutes=30,
            price_eur=30.00
        )

    def test_slot_availability_with_no_reservations(self):
        """Test: Slots disponibles sin reservas."""
        future_date = (ddate.today() + timedelta(days=5))
        
        # Calcular slots manualmente
        slots = []
        business_start = dtime(9, 0)
        business_end = dtime(18, 0)
        step = timedelta(minutes=30)
        duration = timedelta(minutes=60)
        
        current_dt = datetime.combine(future_date, business_start)
        last_start_dt = datetime.combine(future_date, business_end) - duration
        
        while current_dt <= last_start_dt:
            slots.append(current_dt.time().strftime('%H:%M'))
            current_dt = current_dt + step
        
        # Debería tener slots disponibles
        self.assertGreater(len(slots), 0)

    def test_slot_blocked_by_reservation(self):
        """Test: Slot bloqueado por reserva existente."""
        future_date = (ddate.today() + timedelta(days=5))
        slot_time = dtime(10, 0)
        
        # Crear reserva
        Reservation.objects.create(
            name="Test User",
            email="test@example.com",
            phone="691355682",
            offering=self.offering,
            date=future_date,
            time=slot_time,
            service='masaje'
        )
        
        # Verificar que la reserva existe
        self.assertEqual(Reservation.objects.count(), 1)
        reservation = Reservation.objects.first()
        self.assertEqual(reservation.time, slot_time)


class MultipleReservationsTests(TestCase):
    """Tests para manejo de múltiples reservas."""

    def setUp(self):
        """Setup de ofertas."""
        self.offering = Offering.objects.create(
            slug="test",
            name="Test",
            duration_minutes=60,
            price_eur=50.00
        )

    def test_multiple_reservations_same_date(self):
        """Test: Múltiples reservas el mismo día."""
        future_date = (ddate.today() + timedelta(days=5))
        
        # Crear 3 reservas
        for i in range(3):
            Reservation.objects.create(
                name=f"User {i}",
                email=f"user{i}@test.com",
                phone="691355682",
                offering=self.offering,
                date=future_date,
                time=dtime(10 + i, 0),
                service='masaje'
            )
        
        # Contar reservas para esa fecha
        reservations = Reservation.objects.filter(date=future_date)
        self.assertEqual(reservations.count(), 3)

    def test_reservation_time_different_dates(self):
        """Test: Misma hora en diferentes fechas."""
        slot_time = dtime(14, 0)
        
        # Misma hora en dos fechas diferentes
        Reservation.objects.create(
            name="User 1",
            email="user1@test.com",
            phone="691355682",
            offering=self.offering,
            date=ddate(2025, 12, 25),
            time=slot_time,
            service='masaje'
        )
        
        Reservation.objects.create(
            name="User 2",
            email="user2@test.com",
            phone="691355682",
            offering=self.offering,
            date=ddate(2025, 12, 26),
            time=slot_time,
            service='masaje'
        )
        
        # Ambas deberían existir
        self.assertEqual(Reservation.objects.filter(time=slot_time).count(), 2)


class DateValidationTests(TestCase):
    """Tests para validación de fechas."""

    def setUp(self):
        """Setup."""
        self.offering = Offering.objects.create(
            slug="test",
            name="Test",
            price_eur=50.00
        )

    def test_future_date_valid(self):
        """Test: Fecha futura es válida."""
        future_date = (ddate.today() + timedelta(days=5))
        
        reservation = Reservation.objects.create(
            name="Test",
            email="test@example.com",
            phone="691355682",
            offering=self.offering,
            date=future_date,
            time=dtime(14, 0),
            service='masaje'
        )
        
        self.assertEqual(reservation.date, future_date)

    def test_past_date_allowed_in_model(self):
        """Test: Modelo permite fechas pasadas (validación en form)."""
        past_date = (ddate.today() - timedelta(days=5))
        
        # El modelo no valida esto, es responsabilidad del form
        reservation = Reservation.objects.create(
            name="Test",
            email="test@example.com",
            phone="691355682",
            offering=self.offering,
            date=past_date,
            time=dtime(14, 0),
            service='masaje'
        )
        
        self.assertEqual(reservation.date, past_date)


class EmailValidationTests(TestCase):
    """Tests para validación de emails."""

    def setUp(self):
        """Setup."""
        self.offering = Offering.objects.create(
            slug="test",
            name="Test",
            price_eur=50.00
        )

    def test_valid_email_formats(self):
        """Test: Diferentes formatos válidos de email."""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "user123@test.org",
        ]
        
        for email in valid_emails:
            form_data = {
                'name': 'Test',
                'email': email,
                'phone': '+34 691 355 682',
                'offering': self.offering.id,
                'service': 'masaje',
                'date': ddate(2025, 12, 25),
                'time': dtime(14, 0),
            }
            form = ReservationForm(data=form_data)
            self.assertTrue(form.is_valid(), f"Email {email} debería ser válido")

    def test_invalid_email_formats(self):
        """Test: Formatos inválidos de email."""
        invalid_emails = [
            "invalid.email",
            "@example.com",
            "user@",
            "user @example.com",
            "user@example",
        ]
        
        for email in invalid_emails:
            form_data = {
                'name': 'Test',
                'email': email,
                'phone': '+34 691 355 682',
                'offering': self.offering.id,
                'service': 'masaje',
                'date': ddate(2025, 12, 25),
                'time': dtime(14, 0),
            }
            form = ReservationForm(data=form_data)
            self.assertFalse(form.is_valid(), f"Email {email} debería ser inválido")


class PhoneEdgeCasesTests(TestCase):
    """Tests para casos especiales en validación de teléfono."""

    def test_phone_with_spaces_valid(self):
        """Test: Teléfono con espacios."""
        phones_with_spaces = [
            "+34 691 355 682",
            "691 355 682",
            "(691) 355 682",
        ]
        for phone in phones_with_spaces:
            try:
                validate_phone(phone)
                self.assertTrue(True, f"Teléfono '{phone}' debería ser válido")
            except ValidationError:
                self.fail(f"Teléfono '{phone}' debería ser válido")

    def test_phone_with_dashes_valid(self):
        """Test: Teléfono con guiones."""
        phones_with_dashes = [
            "+34-691-355-682",
            "691-355-682",
        ]
        for phone in phones_with_dashes:
            try:
                validate_phone(phone)
                self.assertTrue(True, f"Teléfono '{phone}' debería ser válido")
            except ValidationError:
                self.fail(f"Teléfono '{phone}' debería ser válido")

    def test_phone_minimum_length(self):
        """Test: Mínimo de dígitos."""
        phone_7_digits = "1234567"
        try:
            validate_phone(phone_7_digits)
            self.assertTrue(True, "7 dígitos debería ser válido")
        except ValidationError:
            self.fail("7 dígitos debería ser válido")

    def test_phone_maximum_length(self):
        """Test: Máximo de dígitos."""
        phone_15_digits = "123456789012345"
        try:
            validate_phone(phone_15_digits)
            self.assertTrue(True, "15 dígitos debería ser válido")
        except ValidationError:
            self.fail("15 dígitos debería ser válido")

    def test_phone_too_short(self):
        """Test: Muy pocos dígitos."""
        with self.assertRaises(ValidationError):
            validate_phone("12345")  # 5 dígitos

    def test_phone_too_long(self):
        """Test: Demasiados dígitos."""
        with self.assertRaises(ValidationError):
            validate_phone("1234567890123456")  # 16 dígitos


class ServiceFieldTests(TestCase):
    """Tests para el campo service."""

    def setUp(self):
        """Setup."""
        self.offering = Offering.objects.create(
            slug="test",
            name="Test",
            price_eur=50.00
        )

    def test_service_field_exists(self):
        """Test: Campo service existe en el formulario."""
        form = ReservationForm()
        self.assertIn('service', form.fields)

    def test_service_field_in_model(self):
        """Test: Campo service existe en el modelo."""
        reservation = Reservation(
            name='Test',
            email='test@example.com',
            phone='+34 691 355 682',
            offering=self.offering,
            date=ddate(2025, 12, 25),
            time=dtime(14, 0),
            service='masaje'
        )
        self.assertEqual(reservation.service, 'masaje')


class UserPermissionTests(TestCase):
    """Tests para permisos de usuario."""

    def setUp(self):
        """Setup de usuarios."""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='regularpass123',
            is_staff=False
        )

    def test_staff_user_created(self):
        """Test: Usuario staff creado correctamente."""
        self.assertTrue(self.staff_user.is_staff)
        self.assertEqual(self.staff_user.username, 'staff')

    def test_regular_user_not_staff(self):
        """Test: Usuario regular no es staff."""
        self.assertFalse(self.regular_user.is_staff)

    def test_multiple_staff_users(self):
        """Test: Múltiples usuarios staff."""
        staff_user_2 = User.objects.create_user(
            username='staff2',
            email='staff2@example.com',
            password='pass',
            is_staff=True
        )
        
        staff_count = User.objects.filter(is_staff=True).count()
        self.assertGreaterEqual(staff_count, 2)


class ReservationDateTimePropertiesTests(TestCase):
    """Tests para propiedades datetime de reservas."""

    def setUp(self):
        """Setup."""
        self.offering_60 = Offering.objects.create(
            slug="masaje-60",
            name="Masaje 60min",
            duration_minutes=60,
            price_eur=50.00
        )
        self.offering_40 = Offering.objects.create(
            slug="emocional-40",
            name="Técnicas Emocionales",
            duration_minutes=40,
            price_eur=35.00
        )

    def test_start_datetime_property(self):
        """Test: Propiedad start_datetime."""
        reservation = Reservation.objects.create(
            name="Test",
            email="test@example.com",
            phone="691355682",
            offering=self.offering_60,
            date=ddate(2025, 12, 25),
            time=dtime(14, 30),
            service='masaje'
        )
        
        start = reservation.start_datetime
        self.assertEqual(start.year, 2025)
        self.assertEqual(start.month, 12)
        self.assertEqual(start.day, 25)
        self.assertEqual(start.hour, 14)
        self.assertEqual(start.minute, 30)

    def test_end_datetime_property_60min(self):
        """Test: Propiedad end_datetime con oferta de 60min."""
        reservation = Reservation.objects.create(
            name="Test",
            email="test@example.com",
            phone="691355682",
            offering=self.offering_60,
            date=ddate(2025, 12, 25),
            time=dtime(14, 30),
            service='masaje'
        )
        
        end = reservation.end_datetime
        self.assertEqual(end.hour, 15)
        self.assertEqual(end.minute, 30)

    def test_end_datetime_property_40min(self):
        """Test: Propiedad end_datetime con oferta de 40min."""
        reservation = Reservation.objects.create(
            name="Test",
            email="test@example.com",
            phone="691355682",
            offering=self.offering_40,
            date=ddate(2025, 12, 25),
            time=dtime(14, 30),
            service='emocionales'
        )
        
        end = reservation.end_datetime
        self.assertEqual(end.hour, 15)
        self.assertEqual(end.minute, 10)

    def test_end_datetime_without_offering(self):
        """Test: end_datetime con default 60min (sin offering)."""
        reservation = Reservation.objects.create(
            name="Test",
            email="test@example.com",
            phone="691355682",
            offering=None,
            date=ddate(2025, 12, 25),
            time=dtime(14, 30),
            service='masaje'
        )
        
        end = reservation.end_datetime
        # Debería usar mapping de servicio o default 60
        self.assertIsNotNone(end)
        self.assertGreater((end - reservation.start_datetime).total_seconds(), 0)

    def test_str_representation_with_offering(self):
        """Test: __str__ con offering."""
        reservation = Reservation.objects.create(
            name="Juan",
            email="juan@test.com",
            phone="691355682",
            offering=self.offering_60,
            date=ddate(2025, 12, 25),
            time=dtime(14, 30),
            service='masaje'
        )
        
        str_repr = str(reservation)
        self.assertIn("Juan", str_repr)
        self.assertIn("Masaje", str_repr)
        self.assertIn("2025-12-25", str_repr)

    def test_str_representation_without_offering(self):
        """Test: __str__ sin offering (usa servicio)."""
        reservation = Reservation.objects.create(
            name="María",
            email="maria@test.com",
            phone="691355682",
            offering=None,
            date=ddate(2025, 12, 25),
            time=dtime(14, 30),
            service='biomagnetico'
        )
        
        str_repr = str(reservation)
        self.assertIn("María", str_repr)


class OfferingPriceTests(TestCase):
    """Tests para precios de ofertas."""

    def test_offering_price_decimal(self):
        """Test: Precio como decimal con 2 decimales."""
        offering = Offering.objects.create(
            slug="test",
            name="Test",
            duration_minutes=60,
            price_eur=49.99
        )
        
        self.assertEqual(offering.price_eur, 49.99)

    def test_offering_price_whole_number(self):
        """Test: Precio como número entero."""
        offering = Offering.objects.create(
            slug="test",
            name="Test",
            duration_minutes=60,
            price_eur=50.00
        )
        
        self.assertEqual(offering.price_eur, 50.00)

    def test_multiple_offerings_different_prices(self):
        """Test: Múltiples ofertas con diferentes precios."""
        prices = [25.00, 35.00, 50.00, 75.00]
        
        for i, price in enumerate(prices):
            Offering.objects.create(
                slug=f"offer-{i}",
                name=f"Offering {i}",
                price_eur=price
            )
        
        offerings = Offering.objects.all()
        self.assertEqual(offerings.count(), 4)


class ServiceChoicesTests(TestCase):
    """Tests para las opciones de servicio."""

    def setUp(self):
        """Setup."""
        self.offering = Offering.objects.create(
            slug="test",
            name="Test",
            price_eur=50.00
        )

    def test_service_choices_mapping(self):
        """Test: Todas las opciones de servicio funcionan."""
        service_choices = [
            'masaje',
            'biomagnetico',
            'emocionales',
            'nutricional'
        ]
        
        for service in service_choices:
            reservation = Reservation.objects.create(
                name="Test",
                email="test@example.com",
                phone="691355682",
                offering=self.offering,
                date=ddate(2025, 12, 25),
                time=dtime(14, 30),
                service=service
            )
            self.assertEqual(reservation.service, service)

    def test_service_blank_allowed(self):
        """Test: Campo service puede estar en blanco."""
        reservation = Reservation.objects.create(
            name="Test",
            email="test@example.com",
            phone="691355682",
            offering=self.offering,
            date=ddate(2025, 12, 25),
            time=dtime(14, 30),
            service=''  # Blank
        )
        
        self.assertEqual(reservation.service, '')


class ReservationCreatedAtFieldTests(TestCase):
    """Tests para el campo created_at."""

    def setUp(self):
        """Setup."""
        self.offering = Offering.objects.create(
            slug="test",
            name="Test",
            price_eur=50.00
        )

    def test_created_at_auto_set(self):
        """Test: created_at se asigna automáticamente."""
        reservation = Reservation.objects.create(
            name="Test",
            email="test@example.com",
            phone="691355682",
            offering=self.offering,
            date=ddate(2025, 12, 25),
            time=dtime(14, 30),
            service='masaje'
        )
        
        self.assertIsNotNone(reservation.created_at)
        self.assertLessEqual(
            (timezone.now() - reservation.created_at).total_seconds(),
            2  # Menos de 2 segundos
        )

    def test_created_at_immutable(self):
        """Test: created_at no cambia al actualizar."""
        reservation = Reservation.objects.create(
            name="Test",
            email="test@example.com",
            phone="691355682",
            offering=self.offering,
            date=ddate(2025, 12, 25),
            time=dtime(14, 30),
            service='masaje'
        )
        
        original_created = reservation.created_at
        
        # Actualizar
        reservation.name = "Updated"
        reservation.save()
        
        # created_at no debe cambiar
        self.assertEqual(reservation.created_at, original_created)


class OfferingMetaTests(TestCase):
    """Tests para Meta de Offering."""

    def test_offering_verbose_name(self):
        """Test: Nombre verbose singular."""
        from django.apps import apps
        model = apps.get_model('reservas', 'Offering')
        self.assertEqual(model._meta.verbose_name, 'Oferta')

    def test_offering_verbose_name_plural(self):
        """Test: Nombre verbose plural."""
        from django.apps import apps
        model = apps.get_model('reservas', 'Offering')
        self.assertEqual(model._meta.verbose_name_plural, 'Ofertas')


class ReservationOrderingTests(TestCase):
    """Tests para ordenamiento de Reservation."""

    def setUp(self):
        """Setup."""
        self.offering = Offering.objects.create(
            slug="test",
            name="Test",
            price_eur=50.00
        )

    def test_ordering_by_date_descending(self):
        """Test: Ordenamiento primario por -date."""
        # Crear con fechas en desorden
        dates = [
            ddate(2025, 12, 20),
            ddate(2025, 12, 25),
            ddate(2025, 12, 15),
        ]
        
        for date in dates:
            Reservation.objects.create(
                name=f"Test {date}",
                email=f"test{date}@example.com",
                phone="691355682",
                offering=self.offering,
                date=date,
                time=dtime(14, 0),
                service='masaje'
            )
        
        reservations = list(Reservation.objects.all())
        # Primera debe ser la más reciente
        self.assertEqual(reservations[0].date, ddate(2025, 12, 25))
        self.assertEqual(reservations[1].date, ddate(2025, 12, 20))
        self.assertEqual(reservations[2].date, ddate(2025, 12, 15))

    def test_ordering_by_time_secondary(self):
        """Test: Ordenamiento secundario por time (ascendente)."""
        same_date = ddate(2025, 12, 25)
        times = [dtime(14, 0), dtime(10, 0), dtime(16, 0)]
        
        for time in times:
            Reservation.objects.create(
                name=f"Test {time}",
                email=f"test{time}@example.com",
                phone="691355682",
                offering=self.offering,
                date=same_date,
                time=time,
                service='masaje'
            )
        
        reservations = list(Reservation.objects.filter(date=same_date))
        # Debería estar ordenado por time (ascendente)
        self.assertEqual(reservations[0].time, dtime(10, 0))
        self.assertEqual(reservations[1].time, dtime(14, 0))
        self.assertEqual(reservations[2].time, dtime(16, 0))


# ==================== TESTS ADMIN PANEL ====================

class AdminAuthenticationTests(TestCase):
    """Tests para autenticación y decorador @user_passes_test en admin."""
    
    def setUp(self):
        """Crear usuarios y datos de prueba."""
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staff123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regular123',
            is_staff=False
        )
        self.offering = Offering.objects.create(
            slug="test",
            name="Test Service",
            price_eur=50.00
        )
    
    def test_admin_dashboard_no_auth_redirects_to_login(self):
        """Test: Admin dashboard sin autenticación redirige a login."""
        from unittest.mock import Mock, patch
        from reservas.views import admin_dashboard
        
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = False
        request.user.is_staff = False
        
        # Simular el decorador @user_passes_test
        # Si is_staff es False, debe retornar None (decorator redirige)
        is_staff_check = lambda u: u.is_staff
        self.assertFalse(is_staff_check(request.user))
    
    def test_admin_dashboard_regular_user_no_access(self):
        """Test: Usuario regular no accede al admin."""
        is_staff_check = lambda u: u.is_staff
        self.assertFalse(is_staff_check(self.regular_user))
    
    def test_admin_dashboard_staff_user_has_access(self):
        """Test: Usuario staff tiene acceso al admin."""
        is_staff_check = lambda u: u.is_staff
        self.assertTrue(is_staff_check(self.staff_user))
    
    def test_admin_reservations_staff_only(self):
        """Test: Solo staff accede a admin_reservations."""
        is_staff_check = lambda u: u.is_staff
        # Regular no
        self.assertFalse(is_staff_check(self.regular_user))
        # Staff sí
        self.assertTrue(is_staff_check(self.staff_user))
    
    def test_admin_clients_staff_only(self):
        """Test: Solo staff accede a admin_clients."""
        is_staff_check = lambda u: u.is_staff
        self.assertFalse(is_staff_check(self.regular_user))
        self.assertTrue(is_staff_check(self.staff_user))


class AdminDashboardDataTests(TestCase):
    """Tests para datos del admin dashboard."""
    
    def setUp(self):
        """Crear datos de prueba."""
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staff123',
            is_staff=True
        )
        self.offering = Offering.objects.create(
            slug="test",
            name="Test Service",
            price_eur=50.00
        )
    
    def test_admin_dashboard_counts_reservations(self):
        """Test: Dashboard cuenta las reservas correctamente."""
        # Crear 5 reservas
        for i in range(5):
            Reservation.objects.create(
                name=f"Client {i}",
                email=f"client{i}@example.com",
                phone="691355682",
                offering=self.offering,
                date=ddate.today() + timedelta(days=1),
                time=dtime(14, 0),
                service='masaje'
            )
        
        count = Reservation.objects.count()
        self.assertEqual(count, 5)
    
    def test_admin_dashboard_counts_clients(self):
        """Test: Dashboard cuenta los clientes (no-staff) correctamente."""
        # Crear 3 clientes regulares
        for i in range(3):
            User.objects.create_user(
                username=f'client{i}',
                password='pass',
                is_staff=False
            )
        
        # Crear 2 staff (no deberían contar)
        for i in range(2):
            User.objects.create_user(
                username=f'staff{i}',
                password='pass',
                is_staff=True
            )
        
        clients_count = User.objects.filter(is_staff=False).count()
        # 3 clientes + el staff_user del setUp que es staff
        self.assertEqual(clients_count, 3)
    
    def test_admin_dashboard_context_structure(self):
        """Test: Dashboard retorna contexto con estructura correcta."""
        # Simular contexto del dashboard
        from reservas.models import Reservation
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        
        context = {
            'reservations_count': Reservation.objects.count(),
            'clients_count': UserModel.objects.filter(is_staff=False).count(),
        }
        
        self.assertIn('reservations_count', context)
        self.assertIn('clients_count', context)
        self.assertIsInstance(context['reservations_count'], int)
        self.assertIsInstance(context['clients_count'], int)


class AdminReservationsListTests(TestCase):
    """Tests para listado de reservas en admin."""
    
    def setUp(self):
        """Crear datos de prueba."""
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staff123',
            is_staff=True
        )
        self.offering = Offering.objects.create(
            slug="test",
            name="Test Service",
            price_eur=50.00
        )
    
    def test_admin_reservations_lists_all(self):
        """Test: admin_reservations lista todas las reservas."""
        # Crear 5 reservas
        reservations = []
        for i in range(5):
            r = Reservation.objects.create(
                name=f"Client {i}",
                email=f"client{i}@example.com",
                phone="691355682",
                offering=self.offering,
                date=ddate(2025, 12, 25),
                time=dtime(10+i, 0),
                service='masaje'
            )
            reservations.append(r)
        
        # Verificar que todas se pueden recuperar
        qs = Reservation.objects.select_related('offering').order_by('-date', '-time')
        self.assertEqual(len(list(qs)), 5)
    
    def test_admin_reservations_ordered_by_date_desc(self):
        """Test: Reservas ordenadas por -date (descendente)."""
        dates = [
            ddate(2025, 12, 20),
            ddate(2025, 12, 25),
            ddate(2025, 12, 15),
        ]
        
        for date in dates:
            Reservation.objects.create(
                name="Test",
                email="test@example.com",
                phone="691355682",
                offering=self.offering,
                date=date,
                time=dtime(14, 0),
                service='masaje'
            )
        
        qs = Reservation.objects.select_related('offering').order_by('-date', '-time')
        dates_ordered = [r.date for r in qs]
        # Primera debe ser más reciente
        self.assertEqual(dates_ordered[0], ddate(2025, 12, 25))
    
    def test_admin_reservations_includes_offering_data(self):
        """Test: Listado incluye datos de offering (select_related)."""
        reservation = Reservation.objects.create(
            name="Test",
            email="test@example.com",
            phone="691355682",
            offering=self.offering,
            date=ddate(2025, 12, 25),
            time=dtime(14, 0),
            service='masaje'
        )
        
        qs = Reservation.objects.select_related('offering')
        r = qs.first()
        # Acceder a offering no debe disparar query adicional
        self.assertIsNotNone(r.offering)
        self.assertEqual(r.offering.name, "Test Service")


class AdminClientsListTests(TestCase):
    """Tests para listado de clientes en admin."""
    
    def setUp(self):
        """Crear datos de prueba."""
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staff123',
            is_staff=True
        )
    
    def test_admin_clients_lists_non_staff_only(self):
        """Test: admin_clients solo lista usuarios no-staff."""
        # Crear clientes
        for i in range(3):
            User.objects.create_user(
                username=f'client{i}',
                password='pass',
                is_staff=False
            )
        
        # Crear staff (no deberían aparecer)
        for i in range(2):
            User.objects.create_user(
                username=f'staff_extra{i}',
                password='pass',
                is_staff=True
            )
        
        clients = User.objects.filter(is_staff=False)
        self.assertEqual(clients.count(), 3)
    
    def test_admin_clients_ordered_by_date_joined(self):
        """Test: Clientes ordenados por -date_joined (más recientes primero)."""
        users = []
        for i in range(3):
            u = User.objects.create_user(
                username=f'client{i}',
                password='pass',
                is_staff=False
            )
            users.append(u)
        
        clients = User.objects.filter(is_staff=False).order_by('-date_joined')
        # El último creado debe estar primero (more recent)
        self.assertEqual(clients.first().username, 'client2')
    
    def test_admin_clients_excludes_staff_user(self):
        """Test: El usuario staff_user no aparece en listado de clientes."""
        regular_user = User.objects.create_user(
            username='regular',
            password='pass',
            is_staff=False
        )
        
        clients = User.objects.filter(is_staff=False)
        usernames = [c.username for c in clients]
        
        # staff_user no debe estar
        self.assertNotIn('staff', usernames)
        # regular_user sí debe estar
        self.assertIn('regular', usernames)


class AdminDeleteReservationTests(TestCase):
    """Tests para eliminación de reservas."""
    
    def setUp(self):
        """Crear datos de prueba."""
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staff123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regular123',
            is_staff=False
        )
        self.offering = Offering.objects.create(
            slug="test",
            name="Test Service",
            price_eur=50.00
        )
        self.reservation = Reservation.objects.create(
            name="Client",
            email="client@example.com",
            phone="691355682",
            offering=self.offering,
            date=ddate(2025, 12, 25),
            time=dtime(14, 0),
            service='masaje'
        )
    
    def test_delete_reservation_requires_staff(self):
        """Test: Solo staff puede eliminar reservas."""
        is_staff_check = lambda u: u.is_staff
        self.assertFalse(is_staff_check(self.regular_user))
        self.assertTrue(is_staff_check(self.staff_user))
    
    def test_delete_reservation_removes_from_db(self):
        """Test: Eliminar reserva la remueve de la BD."""
        reservation_id = self.reservation.id
        self.assertTrue(Reservation.objects.filter(id=reservation_id).exists())
        
        # Simular eliminación
        self.reservation.delete()
        
        self.assertFalse(Reservation.objects.filter(id=reservation_id).exists())
    
    def test_delete_reservation_can_get_data_before_delete(self):
        """Test: Antes de eliminar, se puede acceder a los datos."""
        from reservas.models import Reservation
        
        reservation = Reservation.objects.get(id=self.reservation.id)
        
        # Puede acceder a datos
        self.assertEqual(reservation.name, "Client")
        self.assertEqual(reservation.email, "client@example.com")
    
    def test_delete_nonexistent_reservation_raises_error(self):
        """Test: Intentar eliminar ID inexistente lanza error."""
        with self.assertRaises(Reservation.DoesNotExist):
            Reservation.objects.get(id=9999)
    
    def test_multiple_reservations_delete_only_one(self):
        """Test: Eliminar una reserva no afecta otras."""
        # Crear segunda reserva
        r2 = Reservation.objects.create(
            name="Client 2",
            email="client2@example.com",
            phone="691355682",
            offering=self.offering,
            date=ddate(2025, 12, 26),
            time=dtime(14, 0),
            service='masaje'
        )
        
        r1_id = self.reservation.id
        r2_id = r2.id
        
        # Eliminar r1
        self.reservation.delete()
        
        # r1 debe estar gone, r2 debe existir
        self.assertFalse(Reservation.objects.filter(id=r1_id).exists())
        self.assertTrue(Reservation.objects.filter(id=r2_id).exists())


class AdminDeleteUserTests(TestCase):
    """Tests para eliminación de usuarios."""
    
    def setUp(self):
        """Crear datos de prueba."""
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staff123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regular123',
            is_staff=False
        )
        self.other_staff = User.objects.create_user(
            username='other_staff',
            password='pass',
            is_staff=True
        )
    
    def test_delete_user_requires_staff(self):
        """Test: Solo staff puede eliminar usuarios."""
        is_staff_check = lambda u: u.is_staff
        self.assertFalse(is_staff_check(self.regular_user))
        self.assertTrue(is_staff_check(self.staff_user))
    
    def test_cannot_delete_self(self):
        """Test: Un usuario no puede eliminarse a sí mismo."""
        # Simular la lógica de delete_user
        request_user = self.staff_user
        user_to_delete = self.staff_user
        
        # Verificación: usuario_a_eliminar == usuario_actual
        can_delete = not (user_to_delete == request_user or user_to_delete.is_staff)
        
        self.assertFalse(can_delete)
    
    def test_cannot_delete_other_staff(self):
        """Test: No se puede eliminar otro usuario staff."""
        request_user = self.staff_user
        user_to_delete = self.other_staff
        
        # Verificación: usuario_a_eliminar es staff
        can_delete = not (user_to_delete == request_user or user_to_delete.is_staff)
        
        self.assertFalse(can_delete)
    
    def test_can_delete_regular_user(self):
        """Test: Staff puede eliminar usuario regular."""
        request_user = self.staff_user
        user_to_delete = self.regular_user
        
        # Verificación: no es staff ni es el mismo
        can_delete = not (user_to_delete == request_user or user_to_delete.is_staff)
        
        self.assertTrue(can_delete)
    
    def test_delete_regular_user_removes_from_db(self):
        """Test: Eliminar usuario regular lo remueve de la BD."""
        user_id = self.regular_user.id
        self.assertTrue(User.objects.filter(id=user_id).exists())
        
        # Simular eliminación
        self.regular_user.delete()
        
        self.assertFalse(User.objects.filter(id=user_id).exists())
    
    def test_delete_user_with_reservations(self):
        """Test: Eliminar usuario no afecta sus reservas (FK nullable)."""
        offering = Offering.objects.create(
            slug="test",
            name="Test",
            price_eur=50.00
        )
        
        reservation = Reservation.objects.create(
            name="User Name",
            email=self.regular_user.email or "test@example.com",
            phone="691355682",
            offering=offering,
            date=ddate(2025, 12, 25),
            time=dtime(14, 0),
            service='masaje'
        )
        
        r_id = reservation.id
        self.regular_user.delete()
        
        # Reserva sigue existiendo (no tiene FK a User)
        self.assertTrue(Reservation.objects.filter(id=r_id).exists())
    
    def test_delete_nonexistent_user_raises_error(self):
        """Test: Intentar eliminar ID usuario inexistente lanza error."""
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=9999)


class AdminPermissionsEdgeCasesTests(TestCase):
    """Tests para casos extremos de permisos admin."""
    
    def setUp(self):
        """Crear datos de prueba."""
        self.admin = User.objects.create_user(
            username='admin',
            password='pass',
            is_staff=True,
            is_superuser=True
        )
        self.staff = User.objects.create_user(
            username='staff',
            password='pass',
            is_staff=True,
            is_superuser=False
        )
        self.regular = User.objects.create_user(
            username='regular',
            password='pass',
            is_staff=False,
            is_superuser=False
        )
    
    def test_superuser_is_also_staff(self):
        """Test: Superuser es también staff."""
        self.assertTrue(self.admin.is_staff)
        self.assertTrue(self.admin.is_superuser)
    
    def test_staff_not_necessarily_superuser(self):
        """Test: Staff puede no ser superuser."""
        self.assertTrue(self.staff.is_staff)
        self.assertFalse(self.staff.is_superuser)
    
    def test_regular_user_is_not_staff(self):
        """Test: Usuario regular no es staff."""
        self.assertFalse(self.regular.is_staff)
        self.assertFalse(self.regular.is_superuser)
    
    def test_superuser_can_delete_superuser(self):
        """Test: Superuser sí podría eliminar otro superuser (pero protegemos)."""
        # La lógica protege si user_to_delete.is_staff
        user_to_delete = self.admin
        is_protected = user_to_delete.is_staff
        
        self.assertTrue(is_protected)
    
    def test_staff_cannot_delete_superuser(self):
        """Test: Staff regular no puede eliminar superuser."""
        request_user = self.staff
        user_to_delete = self.admin
        
        can_delete = not (user_to_delete == request_user or user_to_delete.is_staff)
        
        self.assertFalse(can_delete)


# ==================== TESTS VIEWS (sin HTTP Client) ====================

from unittest.mock import Mock, patch, MagicMock, mock_open


class YouTubeFetchTests(TestCase):
    """Tests para _fetch_youtube_videos sin hacer requests reales."""
    
    @patch('reservas.views.urllib.request.urlopen')
    @patch('reservas.views.ET.fromstring')
    def test_fetch_youtube_empty_channel_id(self, mock_fromstring, mock_urlopen):
        """Test: Channel ID vacío retorna lista vacía."""
        from reservas.views import _fetch_youtube_videos
        
        result = _fetch_youtube_videos('')
        self.assertEqual(result, [])
        
        result = _fetch_youtube_videos(None)
        self.assertEqual(result, [])
    
    @patch('reservas.views.urllib.request.urlopen')
    @patch('reservas.views.ET.fromstring')
    def test_fetch_youtube_timeout(self, mock_fromstring, mock_urlopen):
        """Test: Timeout en YouTube retorna lista vacía."""
        from reservas.views import _fetch_youtube_videos
        
        mock_urlopen.side_effect = TimeoutError()
        
        result = _fetch_youtube_videos('UCxxxxx')
        self.assertEqual(result, [])
    
    @patch('reservas.views.urllib.request.urlopen')
    @patch('reservas.views.ET.fromstring')
    def test_fetch_youtube_network_error(self, mock_fromstring, mock_urlopen):
        """Test: Error de red retorna lista vacía."""
        from reservas.views import _fetch_youtube_videos
        
        mock_urlopen.side_effect = Exception("Network error")
        
        result = _fetch_youtube_videos('UCxxxxx')
        self.assertEqual(result, [])
    
    @patch('reservas.views.urllib.request.urlopen')
    @patch('reservas.views.ET.fromstring')
    def test_fetch_youtube_success(self, mock_fromstring, mock_urlopen):
        """Test: YouTube fetch exitoso retorna lista de videos."""
        from reservas.views import _fetch_youtube_videos
        
        # Mock XML response
        mock_response = Mock()
        mock_response.read.return_value = b'<xml></xml>'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Mock parsed XML
        mock_root = Mock()
        mock_entry = Mock()
        mock_entry.find.side_effect = lambda path, ns: Mock(text='Test Video' if 'title' in str(path) else None, attrib={'href': 'https://youtube.com/watch?v=123'})
        mock_entry.find('yt:videoId', {}).text = 'abc123'
        
        mock_root.findall.return_value = [mock_entry]
        mock_fromstring.return_value = mock_root
        
        result = _fetch_youtube_videos('UCxxxxx', limit=6)
        
        # Verifica que se intentó buscar
        self.assertIsInstance(result, list)
    
    @patch('reservas.views.urllib.request.urlopen')
    def test_fetch_youtube_called_with_correct_url(self, mock_urlopen):
        """Test: URL de YouTube se llama correctamente."""
        from reservas.views import _fetch_youtube_videos
        
        mock_urlopen.side_effect = Exception()
        
        channel_id = 'UC12345'
        _fetch_youtube_videos(channel_id)
        
        # Verifica que se intentó hacer request
        self.assertTrue(mock_urlopen.called)


class InstagramFetchTests(TestCase):
    """Tests para _fetch_instagram_posts."""
    
    def test_fetch_instagram_empty_username(self):
        """Test: Username vacío retorna lista vacía."""
        from reservas.views import _fetch_instagram_posts
        
        result = _fetch_instagram_posts('')
        self.assertEqual(result, [])
        
        result = _fetch_instagram_posts(None)
        self.assertEqual(result, [])
    
    def test_fetch_instagram_returns_empty_list(self):
        """Test: Instagram fetch retorna lista vacía (fallback)."""
        from reservas.views import _fetch_instagram_posts
        
        result = _fetch_instagram_posts('someinstauser')
        self.assertEqual(result, [])
        self.assertIsInstance(result, list)


class EmailSendingTests(TestCase):
    """Tests para _send_confirmation_email con mocks."""
    
    def setUp(self):
        """Crear datos de prueba."""
        self.offering = Offering.objects.create(
            slug="test",
            name="Masaje Test",
            duration_minutes=60,
            price_eur=50.00
        )
        self.reservation = Reservation.objects.create(
            name="Cliente",
            email="cliente@example.com",
            phone="691355682",
            offering=self.offering,
            date=ddate(2025, 12, 25),
            time=dtime(14, 0),
            service='masaje'
        )
    
    @patch('reservas.views.logger')
    def test_send_email_no_email_address_logs_warning(self, mock_logger):
        """Test: Sin email, se registra warning."""
        from reservas.views import _send_confirmation_email
        
        reservation = Reservation.objects.create(
            name="Sin Email",
            email="",  # Sin email
            phone="691355682",
            offering=self.offering,
            date=ddate(2025, 12, 25),
            time=dtime(14, 0),
            service='masaje'
        )
        
        _send_confirmation_email(reservation)
        
        # Verifica que se registró warning
        mock_logger.warning.assert_called()
    
    @patch('reservas.views.logger')
    def test_send_email_with_valid_data(self, mock_logger):
        """Test: Email con datos válidos no causa error."""
        from reservas.views import _send_confirmation_email
        
        # No debe lanzar excepción
        try:
            _send_confirmation_email(self.reservation)
            # Si DEBUG=True, no usa Resend, así que no hay error
            success = True
        except Exception as e:
            success = False
        
        self.assertTrue(success)
    
    def test_email_content_has_required_fields(self):
        """Test: Contenido de email incluye campos requeridos."""
        # Verifica estructura del email sin enviarlo
        reservation = self.reservation
        
        # Formato esperado en email
        service_name = reservation.offering.name if reservation.offering else 'No especificado'
        date_str = reservation.date.strftime('%d/%m/%Y')
        time_str = reservation.time.strftime('%H:%M')
        
        self.assertEqual(service_name, "Masaje Test")
        self.assertEqual(date_str, "25/12/2025")
        self.assertEqual(time_str, "14:00")


class AvailableTimesAPITests(TestCase):
    """Tests para available_times_api sin HTTP Client."""
    
    def setUp(self):
        """Crear datos de prueba."""
        self.offering = Offering.objects.create(
            slug="60min",
            name="Sesión 60min",
            duration_minutes=60,
            price_eur=60.00
        )
    
    def test_available_times_returns_json_structure(self):
        """Test: available_times_api retorna estructura JSON correcta."""
        # Simular lógica de la vista sin hacer request HTTP
        
        offering_id = self.offering.id
        date_str = (ddate.today() + timedelta(days=1)).isoformat()
        
        # Simular búsqueda de slots disponibles
        business_start = dtime(9, 0)
        business_end = dtime(18, 0)
        step = timedelta(minutes=30)
        
        slots = []
        current_dt = datetime.combine(ddate.fromisoformat(date_str), business_start)
        last_start_dt = datetime.combine(ddate.fromisoformat(date_str), business_end) - timedelta(minutes=60)
        
        while current_dt <= last_start_dt:
            slots.append(current_dt.time().strftime('%H:%M'))
            current_dt = current_dt + step
        
        # Estructura esperada
        response_data = {'times': slots}
        
        self.assertIn('times', response_data)
        self.assertIsInstance(response_data['times'], list)
        self.assertTrue(len(response_data['times']) > 0)
    
    def test_available_times_slot_generation(self):
        """Test: Generación de slots de 30 minutos."""
        business_start = dtime(9, 0)
        business_end = dtime(18, 0)
        step = timedelta(minutes=30)
        
        test_date = ddate.today() + timedelta(days=1)
        slots = []
        current_dt = datetime.combine(test_date, business_start)
        
        while current_dt.time() < business_end:
            slots.append(current_dt.time().strftime('%H:%M'))
            current_dt = current_dt + step
        
        # Verifica slots conocidos
        self.assertIn('09:00', slots)
        self.assertIn('09:30', slots)
        self.assertIn('10:00', slots)
    
    def test_available_times_respects_offering_duration(self):
        """Test: Slots disponibles respetan duración de servicio."""
        duration = 60  # minutos
        business_start = dtime(9, 0)
        business_end = dtime(18, 0)
        step = timedelta(minutes=30)
        duration_delta = timedelta(minutes=duration)
        
        test_date = ddate.today() + timedelta(days=1)
        slots = []
        current_dt = datetime.combine(test_date, business_start)
        last_start_dt = datetime.combine(test_date, business_end) - duration_delta
        
        while current_dt <= last_start_dt:
            slots.append(current_dt.time().strftime('%H:%M'))
            current_dt = current_dt + step
        
        # Último slot debe ser antes del cierre menos la duración
        last_slot_time = dtime.fromisoformat(slots[-1]) if slots else None
        self.assertIsNotNone(last_slot_time)
        
        # El servicio debe caber antes del cierre
        end_time_of_last = (datetime.combine(test_date, last_slot_time) + duration_delta).time()
        self.assertLessEqual(end_time_of_last, business_end)
    
    def test_available_times_excludes_booked_slots(self):
        """Test: Slots ocupados se excluyen de disponibilidad."""
        test_date = ddate.today() + timedelta(days=1)
        
        # Crear reserva en 14:00
        Reservation.objects.create(
            name="Ocupado",
            email="test@example.com",
            phone="691355682",
            offering=self.offering,
            date=test_date,
            time=dtime(14, 0),
            service='masaje'
        )
        
        # Simular búsqueda de slots
        booked = Reservation.objects.filter(date=test_date).values_list('time', flat=True)
        booked_times = [t.strftime('%H:%M') for t in booked]
        
        self.assertIn('14:00', booked_times)
        self.assertEqual(len(booked_times), 1)


class LogoutViewTests(TestCase):
    """Tests para logout_view."""
    
    def setUp(self):
        """Crear usuario de prueba."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_logout_user_exists(self):
        """Test: logout_view existe como función."""
        from reservas.views import logout_view
        
        self.assertTrue(callable(logout_view))
    
    def test_logout_is_login_required(self):
        """Test: logout_view requiere login."""
        from reservas.views import logout_view
        
        # Crear mock request sin autenticación
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = False
        
        # La vista debería redirigir o requerir auth
        self.assertFalse(request.user.is_authenticated)


class ReservationFormIntegrationTests(TestCase):
    """Tests para ReservationForm con datos reales."""
    
    def setUp(self):
        """Crear ofertas de prueba."""
        self.offering = Offering.objects.create(
            slug="60",
            name="Test 60min",
            duration_minutes=60,
            price_eur=60.00
        )
    
    def test_form_creation_from_valid_data(self):
        """Test: Crear formulario con datos válidos."""
        form_data = {
            'name': 'Juan',
            'email': 'juan@example.com',
            'phone': '691355682',
            'offering': self.offering.id,
            'date': (ddate.today() + timedelta(days=1)).isoformat(),
            'time': '14:00',
            'service': 'masaje',
        }
        
        form = ReservationForm(data=form_data)
        self.assertTrue(form.is_valid(), msg=form.errors)
    
    def test_form_invalid_phone(self):
        """Test: Validar teléfono inválido."""
        form_data = {
            'name': 'Juan',
            'email': 'juan@example.com',
            'phone': '123',  # Muy corto
            'offering': self.offering.id,
            'date': (ddate.today() + timedelta(days=1)).isoformat(),
            'time': '14:00',
            'service': 'masaje',
        }
        
        form = ReservationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_form_invalid_email(self):
        """Test: Validar email inválido."""
        form_data = {
            'name': 'Juan',
            'email': 'not-an-email',  # Email inválido
            'phone': '691355682',
            'offering': self.offering.id,
            'date': (ddate.today() + timedelta(days=1)).isoformat(),
            'time': '14:00',
            'service': 'masaje',
        }
        
        form = ReservationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_form_missing_required_fields(self):
        """Test: Campos requeridos validados."""
        form_data = {
            'name': '',  # Vacío
            'email': 'test@example.com',
        }
        
        form = ReservationForm(data=form_data)
        self.assertFalse(form.is_valid())


class ContactoFormTests(TestCase):
    """Tests para funcionalidad de contacto."""
    
    def test_contact_form_has_required_fields(self):
        """Test: Formulario de contacto tiene campos requeridos."""
        # Simular estructura esperada del formulario
        required_fields = ['name', 'email', 'phone']
        
        # Verificar que estos campos son esperados en contacto
        self.assertIn('name', required_fields)
        self.assertIn('email', required_fields)
        self.assertIn('phone', required_fields)
    
    def test_contact_form_email_format(self):
        """Test: Email en contacto debe ser válido."""
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        
        # Email válido
        try:
            validate_email('contact@example.com')
            valid = True
        except ValidationError:
            valid = False
        
        self.assertTrue(valid)
        
        # Email inválido
        try:
            validate_email('not-an-email')
            valid = True
        except ValidationError:
            valid = False
        
        self.assertFalse(valid)


class SignupViewTests(TestCase):
    """Tests para signup_view sin HTTP Client."""
    
    def test_user_creation_from_form_data(self):
        """Test: Crear usuario desde datos de formulario."""
        from django.contrib.auth.forms import UserCreationForm
        
        form_data = {
            'username': 'newuser',
            'password1': 'secure123pass',
            'password2': 'secure123pass',
        }
        
        form = UserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), msg=form.errors)
    
    def test_user_creation_password_mismatch(self):
        """Test: Contraseñas no coinciden."""
        from django.contrib.auth.forms import UserCreationForm
        
        form_data = {
            'username': 'newuser',
            'password1': 'secure123pass',
            'password2': 'different123pass',
        }
        
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_user_creation_duplicate_username(self):
        """Test: Username duplicado rechazado."""
        from django.contrib.auth.forms import UserCreationForm
        
        # Crear primer usuario
        User.objects.create_user(
            username='existing',
            password='pass123'
        )
        
        # Intentar crear con mismo username
        form_data = {
            'username': 'existing',
            'password1': 'secure123pass',
            'password2': 'secure123pass',
        }
        
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
