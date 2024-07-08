#!/usr/bin/env bash

# Exit on error
set -o errexit

# Upgrade pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Collect static files and run migrations
python manage.py collectstatic --no-input
python manage.py migrate

# Create a superuser if it doesn't exist
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='$ADMIN_USERNAME').exists() or User.objects.create_superuser('$ADMIN_USERNAME', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')" | python manage.py shell