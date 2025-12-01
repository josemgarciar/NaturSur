#!/usr/bin/env python3
import os
import sys

# Ajustar sys.path y settings para poder ejecutarlo desde scripts/
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "natursur.settings")

import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

USERNAME = os.environ.get("ADMINUSER", "admin")
PASSWORD = os.environ.get("ADMINPASS", "adminpass")
EMAIL = os.environ.get("ADMINEMAIL", "admin@example.com")

if not User.objects.filter(username=USERNAME).exists():
    User.objects.create_superuser(username=USERNAME, email=EMAIL, password=PASSWORD)
    print(f"Created superuser {USERNAME}")
else:
    print("Superuser already exists")
