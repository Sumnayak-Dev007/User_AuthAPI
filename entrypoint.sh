#!/usr/bin/env bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for Postgres..."
while ! nc -z "$POSTGRES_HOST" "${POSTGRES_PORT:-5432}"; do
  sleep 0.5
done
echo "Postgres started"

# Run Django migrations
python manage.py migrate --noinput

# Create superuser if environment variables are provided
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  echo "Creating superuser..."
  python manage.py shell -c "from django.contrib.auth import get_user_model;
User = get_user_model();
username='$DJANGO_SUPERUSER_USERNAME';
email='$DJANGO_SUPERUSER_EMAIL';
password='$DJANGO_SUPERUSER_PASSWORD';
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)"
fi

# Collect static files (optional, for production)
python manage.py collectstatic --noinput

# Start Gunicorn server
exec gunicorn user_auth_api.wsgi:application --bind 0.0.0.0:8000
