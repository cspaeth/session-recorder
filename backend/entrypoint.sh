#!/bin/bash

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-ssr.settings}"

if [ ! -e "/env/bin/activate" ]; then
    virtualenv /env --no-site-packages
    /env/bin/pip install -r /src/requirements.txt
fi

. /env/bin/activate
python setup.py develop

manage.py updatesite

COLLECTSTATIC="${COLLECTSTATIC:-True}"
if [ "$COLLECTSTATIC" == "True" ]; then
    echo "Collecting ..."
    manage.py collectstatic <<<yes
fi

MIGRATE="${MIGRATE:-False}"
if [ "$MIGRATE" = "True" ]; then
    echo "Migrating ..."
    manage.py migrate;
fi

CRONJOBS="${CRONJOBS:-False}"
if [ "$CRONJOBS" = "True" ]; then
    echo "Configuring cronjobs ..."
    echo "$(env ; crontab -l)" | crontab -
    service cron start
    manage.py crontab add
fi

DEVSERVER="${DEVSERVER:-False}"

touch /logs/django.log
tail -n 0 -F /logs/django.log &

if [ "$DEBUG" == "DEBUG" ] || [ "$DEVSERVER" == "True" ]; then
    echo "Starting manage.py runserver..."
    manage.py runserver 0.0.0.0:8000 "$@";
else
    echo "Compressing Assets..."
    manage.py compress

    # Prepare log files
    touch /logs/gunicorn.log
    touch /logs/gunicorn-access.log

    echo "Starting Gunicorn..."
    exec gunicorn spiralstudio.wsgi:application \
        --name spiralstudio \
        --bind 0.0.0.0:8000 \
        --workers 5 \
        --log-level=info \
        --log-file=/logs/gunicorn.log \
        --access-logfile=/logs/gunicorn-access.log \
    "$@"
fi