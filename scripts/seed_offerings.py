import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'natursur.settings')
django.setup()

from reservas.models import Offering

DATA = [
    {'slug': 'sesion-40', 'name': "Sesión 40'", 'duration_minutes': 40, 'price_eur': Decimal('28.00')},
    {'slug': 'sesion-60', 'name': "Sesión 60'", 'duration_minutes': 60, 'price_eur': Decimal('45.00')},
    {'slug': 'sesion-90', 'name': "Sesión 90'", 'duration_minutes': 90, 'price_eur': Decimal('70.00')},
    {'slug': 'paquete-3x40', 'name': "3 sesiones de 40'", 'duration_minutes': 40, 'price_eur': Decimal('70.00')},
    {'slug': 'premium-60', 'name': "Sesión Premium 60'", 'duration_minutes': 60, 'price_eur': Decimal('50.00')},
    {'slug': 'domicilio-60', 'name': "Domicilio 60'", 'duration_minutes': 60, 'price_eur': Decimal('100.00')},
]

for item in DATA:
    obj, created = Offering.objects.get_or_create(slug=item['slug'], defaults=item)
    if created:
        print('Created', obj)
    else:
        # update price/duration if changed
        changed = False
        if obj.price_eur != item['price_eur']:
            obj.price_eur = item['price_eur']; changed = True
        if obj.duration_minutes != item['duration_minutes']:
            obj.duration_minutes = item['duration_minutes']; changed = True
        if changed:
            obj.save(); print('Updated', obj)
        else:
            print('Exists', obj)

print('Done')
