#!/bin/bash

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-ssr.settings}"

if [ ! -e "/env/bin/activate" ]; then
    virtualenv /env --no-site-packages
    /env/bin/pip install -r /src/requirements.txt
fi

. /env/bin/activate
python setup.py develop

manage.py runworker processuploads