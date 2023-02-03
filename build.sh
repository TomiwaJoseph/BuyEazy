#!/usr/bin/env bash

set -o errexit  # exit on error

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate
python manage.py createsu
python manage.py loaddata db.json