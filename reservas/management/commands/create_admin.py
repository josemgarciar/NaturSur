from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = 'Create an admin user if it does not exist. Uses environment variables or prompts for input.'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the admin user')
        parser.add_argument('--email', type=str, help='Email for the admin user')
        parser.add_argument('--password', type=str, help='Password for the admin user')

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get values from options, environment variables, or defaults
        username = options.get('username') or os.getenv('ADMIN_USERNAME', 'admin')
        email = options.get('email') or os.getenv('ADMIN_EMAIL', 'admin@natursur.com')
        password = options.get('password') or os.getenv('ADMIN_PASSWORD', 'admin123')

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'⚠️  Usuario "{username}" ya existe.'))
            return

        try:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'✅ Usuario admin "{username}" creado exitosamente'))
            self.stdout.write(self.style.SUCCESS(f'   Email: {email}'))
            self.stdout.write(self.style.WARNING(f'   ⚠️  Cambia la contraseña después de la primera sesión'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))

