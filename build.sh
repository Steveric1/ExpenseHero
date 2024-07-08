#!/usr/bin/env bash

# Exit on error
set -o errexit

# Update and install system dependencies
apt-get update
apt-get install -y build-essential libffi-dev python3-dev

# Clean up
apt-get clean

# Upgrade pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Collect static files and run migrations
python manage.py collectstatic --no-input
python manage.py migrate
