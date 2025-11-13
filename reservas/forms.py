from django import forms
from .models import Reservation
from django.utils import timezone
from .models import Reservation as ReservationModel
from datetime import datetime, timedelta


class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


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
        }
        labels = {
            'name': 'Nombre',
            'email': 'Correo electrónico',
            'phone': 'Teléfono',
            'service': 'Servicio',
            'date': 'Fecha',
            'time': 'Hora',
            'notes': 'Notas',
        }

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
