#!/bin/sh

python manage.py run_redis_worker &
python manage.py runserver
