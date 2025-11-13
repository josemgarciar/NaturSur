from django.db import models
from datetime import datetime, timedelta, time as dtime


class Offering(models.Model):
    """Servicio/oferta: duración en minutos y precio en euros."""
    slug = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=120)
    duration_minutes = models.PositiveIntegerField(default=60)
    price_eur = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        verbose_name = "Oferta"
        verbose_name_plural = "Ofertas"

    def __str__(self) -> str:
        return f"{self.name} — {self.duration_minutes}′ — €{self.price_eur}"


class Reservation(models.Model):
    SERVICE_CHOICES = [
        ("masaje", "Masaje y Osteopatía"),
        ("biomagnetico", "Par Biomagnético"),
        ("emocionales", "Técnicas Emocionales"),
        ("nutricional", "Asesoramiento Nutricional y Estilo de Vida"),
    ]

    name = models.CharField("Nombre", max_length=100)
    email = models.EmailField("Email")
    phone = models.CharField("Teléfono", max_length=20)
    # Legacy: SERVICE_CHOICES kept for compatibility, but prefer `offering`.
    service = models.CharField("Servicio", max_length=20, choices=SERVICE_CHOICES, blank=True)
    offering = models.ForeignKey('reservas.Offering', null=True, blank=True, on_delete=models.SET_NULL, related_name='reservations')
    date = models.DateField("Fecha")
    time = models.TimeField("Hora")
    notes = models.TextField("Notas", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ["-date", "time"]

    def __str__(self) -> str:
        label = self.get_service_display() if self.offering is None else self.offering.name
        return f"{self.name} - {label} ({self.date} {self.time})"

    @property
    def start_datetime(self) -> datetime:
        return datetime.combine(self.date, self.time)

    @property
    def end_datetime(self) -> datetime:
        minutes = 60
        if self.offering and self.offering.duration_minutes:
            minutes = int(self.offering.duration_minutes)
        elif self.service:
            # best-effort mapping from legacy choices
            mapping = {'masaje': 60, 'biomagnetico': 60, 'emocionales': 40, 'nutricional': 60}
            minutes = mapping.get(self.service, 60)
        return self.start_datetime + timedelta(minutes=minutes)
