from django import forms
from .models import Reservation
from django.utils import timezone
from .models import Reservation as ReservationModel
from datetime import datetime, timedelta
import re
from django.core.exceptions import ValidationError


class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


def validate_phone(value):
    """Valida que el teléfono sea un número válido (7-15 dígitos)."""
    # Elimina espacios, guiones, paréntesis y el símbolo +
    cleaned = re.sub(r'[\s\-\(\)\+]', '', value)
    # Verifica que solo contenga dígitos
    if not cleaned.isdigit():
        raise ValidationError('El teléfono solo puede contener dígitos, espacios, guiones o paréntesis.')
    # Verifica que tenga una longitud válida (7-15 dígitos)
    if len(cleaned) < 7 or len(cleaned) > 15:
        raise ValidationError('El teléfono debe tener entre 7 y 15 dígitos.')


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'name', 'email', 'phone', 'offering', 'service', 'date', 'time', 'notes'
        ]
        widgets = {
            'date': DateInput(),
            'time': TimeInput(),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'phone': forms.TextInput(attrs={'placeholder': '+34 XXX XXX XXX'}),
        }
        labels = {
            'name': 'Nombre',
            'email': 'Correo electrónico',
            'phone': 'Teléfono',
            'offering': 'Oferta',
            'service': 'Servicio',
            'date': 'Fecha',
            'time': 'Hora',
            'notes': 'Notas',
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone:
            validate_phone(phone)
        return phone

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date:
            # Verificar que no sea fin de semana (5=sábado, 6=domingo)
            if date.weekday() in [5, 6]:
                raise ValidationError('No se pueden hacer reservas en fin de semana. Por favor, elige un día entre semana.')
        return date

    def clean(self):
        cleaned = super().clean()
        offering = cleaned.get('offering')
        date = cleaned.get('date')
        time = cleaned.get('time')
        if not date or not time:
            return cleaned

        # compute start and end
        start_dt = timezone.make_aware(datetime.combine(date, time)) if timezone.is_naive(datetime.combine(date, time)) else datetime.combine(date, time)
        duration = 60
        if offering and offering.duration_minutes:
            duration = int(offering.duration_minutes)
        end_dt = start_dt + timedelta(minutes=duration)

        # check overlaps: any existing reservation whose interval intersects
        qs = ReservationModel.objects.filter(date=date).exclude(pk=self.instance.pk if self.instance else None)
        for r in qs:
            r_start = timezone.make_aware(datetime.combine(r.date, r.time)) if timezone.is_naive(datetime.combine(r.date, r.time)) else datetime.combine(r.date, r.time)
            r_end = r_start + timedelta(minutes=(r.offering.duration_minutes if r.offering else 60))
            # overlap if start < r_end and r_start < end
            if (start_dt < r_end) and (r_start < end_dt):
                raise forms.ValidationError('El horario seleccionado se solapa con otra reserva. Elige otra hora.')

        return cleaned
