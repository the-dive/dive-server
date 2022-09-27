#!/bin/bash

/code/scripts/wait-for-it.sh $DATABASE_HOSTNAME:$DATABASE_PORT && python manage.py runserver 0.0.0.0:8000
