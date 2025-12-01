release: python manage.py migrate
web: gunicorn natursur.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60
