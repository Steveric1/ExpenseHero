#!/usr/bin/env bash

# Exit on error
set -o errexit

apt-get update && apt-get install -y build-essential libffi-dev

pip install --upgrade pip

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

python manage.py collectstatic  --no-input
python manage.py migrate 