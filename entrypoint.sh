#!/usr/bin/env bash
set -e

# wait for DB to be ready (simple loop)
echo "Waiting for postgres..."
while ! nc -z "$POSTGRES_HOST" "${POSTGRES_PORT:-5432}"; do
  sleep 0.5
done
echo "Postgres started"

# run migrations
python manage.py migrate --noinput

# create superuser automatically if env provided
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  echo "Creating superuser..."
  python manage.py shell - <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
username = "$DJANGO_SUPERUSER_USERNAME"
email = "$DJANGO_SUPERUSER_EMAIL"
password = "$DJANGO_SUPERUSER_PASSWORD"
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
EOF
fi

# collect static (optional)
# python manage.py collectstatic --noinput

# start gunicorn
exec gunicorn authapi.wsgi:application --bind 0.0.0.0:8000
