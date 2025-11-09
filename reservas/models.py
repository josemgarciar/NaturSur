from django.db import models


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
    service = models.CharField("Servicio", max_length=20, choices=SERVICE_CHOICES)
    date = models.DateField("Fecha")
    time = models.TimeField("Hora")
    notes = models.TextField("Notas", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ["-date", "time"]

    def __str__(self) -> str:
        return f"{self.name} - {self.get_service_display()} ({self.date} {self.time})"
