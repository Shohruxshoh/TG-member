#!/bin/bash

echo "🔧 Migrations boshlandi..."
python manage.py makemigrations --noinput

echo "🔧 Migrate boshlandi..."
python manage.py migrate --noinput

echo "🧑‍💻 Superuser tekshirilmoqda..."
python manage.py shell <<EOF
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin1")
email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123")

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("✅ Superuser yaratildi.")
else:
    print("ℹ️  Superuser allaqachon mavjud.")
EOF

echo "🚀 Gunicorn ishga tushmoqda..."

exec "$@"