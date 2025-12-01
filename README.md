# NaturSur · Cuidado y Bienestar (Django)

Proyecto base en Django para el sitio "NaturSur" con:

- Página de inicio con diseño moderno (HTML + CSS)
- Formulario de reservas (modelo + formulario + vistas)
- Página de confirmación de reserva
- Página de tienda online (demo) accesible con un botón

## Requisitos

- Python 3.10+

## Instalación y ejecución

```bash
# 1) Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 2) Instalar dependencias
pip install -r requirements.txt

# 3) Migraciones de base de datos
python manage.py migrate

# (Opcional) Crear superusuario para admin
python manage.py createsuperuser

# 4) Arrancar el servidor
python manage.py runserver
```
En bash o zsh

```bash
python3 -m venv .venv
source .venv/bin/activate

scripts/start_dev.sh
```
o windows

```bash
python3 -m venv .venv
source .venv/bin/activate

scripts/start_dev.bat
```


Visita http://127.0.0.1:8000 para ver la web.

Panel de administración: http://127.0.0.1:8000/admin

## Estructura principal

- `natursur/` – configuración del proyecto Django
- `reservas/` – app con modelos, formularios, vistas, urls, plantillas y estáticos
	- `templates/reservas/` – `base.html`, `home.html`, `booking_success.html`, `tienda.html`
	- `static/reservas/css/style.css` – estilos del sitio

## Personalización rápida

- Cambia servicios disponibles en `reservas/models.py` (`SERVICE_CHOICES`).
- Ajusta estilos en `reservas/static/reservas/css/style.css`.
- Para desplegar, genera un `SECRET_KEY` seguro y desactiva `DEBUG` en `natursur/settings.py`.

## Próximos pasos (sugerencias)

- Añadir disponibilidad y validaciones de solapamiento de reservas.
- Email de confirmación con `django.core.mail`.
- Carrito real en la tienda (por ejemplo, Django Oscar, Django-SHOP o integración de Stripe Checkout).
