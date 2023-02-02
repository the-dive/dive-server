#!/bin/bash

python3 manage.py migrate --no-input

#celery -A dive worker --loglevel=info
python3 manage.py run_celery_dev &
python3 manage.py runserver 0.0.0.0:8000

