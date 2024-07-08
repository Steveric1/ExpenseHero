#!/usr/bin/env bash

# Exit on error
set -o errexit

# Install system dependencies
apt-get install --no-install-recommends -y build-essential libffi-dev python3-dev

# Upgrade pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Collect static files and run migrations
python manage.py collectstatic --no-input
python manage.py migrate