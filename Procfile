web: gunicorn tarabaintel.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
web: python manage.py collectstatic --noinput && gunicorn tarabaintel.wsgi:application --bind 0.0.0.0:$PORT
