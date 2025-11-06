from django import forms
from .models import Reservation


class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'name', 'email', 'phone', 'service', 'date', 'time', 'notes'
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
