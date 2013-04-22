#!/bin/bash

set -e

: ${VIRTUAL_ENV:?"This script needs to be run inside of an activated virtualenv"}

PROJECT_NAME=$(basename $VIRTUAL_ENV)

pip install "django<1.6"

django-admin.py startproject --template=https://github.com/ulope/django-template/archive/master.zip --extension=py,key $PROJECT_NAME

cd $PROJECT_NAME

pip install -r reqs/default.txt
pip install -r reqs/dev.txt

chmod +x manage.py

find . -type f -name ".keep" | xargs rm
rm mkproject.sh
rm README
