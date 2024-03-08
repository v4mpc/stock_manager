#!/bin/sh

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createadminuser

gunicorn \
  --bind 0.0.0.0:8000 \
  --workers=1 \
  --worker-class "${SERVER_WORKER_CLASS:-gthread}" \
  --threads "${SERVER_THREADS_AMOUNT:-20}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  itn_portal.wsgi:application
