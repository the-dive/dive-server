#!/bin/bash

python3 manage.py migrate --no-input
python3 manage.py run_celery_dev &
gunicorn -w 4 -b 0.0.0.0:8000 dive.wsgi:application
