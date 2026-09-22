#!/bin/bash

# Collect static files
python manage.py collectstatic --noinput --clear

# Apply migrations
python manage.py migrate --noinput

# Start server
gunicorn tarabaintel.wsgi:application --bind 0.0.0.0:$PORT