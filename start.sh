#!/bin/bash

# 1. Force collect and clear old static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --clear

# 2. Apply database migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# 3. Start the server
echo "🚀 Starting Gunicorn server..."
gunicorn tarabaintel.wsgi:application --bind 0.0.0.0:$PORT