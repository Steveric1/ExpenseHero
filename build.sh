#!/usr/bin/env bash

# Exit on error
set -o errexit

# Update and install system dependencies
apt-get update
apt-get install -y build-essential libffi-dev

# Clean up
apt-get clean
rm -rf /var/lib/apt/lists/*

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

python manage.py collectstatic  --no-input
python manage.py migrate 