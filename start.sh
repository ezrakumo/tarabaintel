#!/bin/bash

# 1. Apply all pending database migrations safely
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# 2. Start the Gunicorn web server
echo "🚀 Starting Gunicorn server..."
gunicorn tarabaintel.wsgi:application --bind 0.0.0.0:$PORT