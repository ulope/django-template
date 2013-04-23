#!/bin/bash

set -e

: ${VIRTUAL_ENV:?"This script needs to be run inside of an activated virtualenv"}
PROJECT_NAME=${1:-$(basename $VIRTUAL_ENV)}

echo "Bootstrapping project '$PROJECT_NAME':"

echo -n   " - Installing Django..."
pip install "Django<1.6" > /dev/null
echo -e "\r - Successfully installed Django."

echo -n   " - Setting up Django project..."
django-admin.py startproject --template=https://github.com/ulope/django-template/archive/master.zip --extension=py,key $PROJECT_NAME
echo -e "\r - Done setting up Django project"

cd $PROJECT_NAME

git init > /dev/null

echo -n   " - Installing dependencies..."
pip install -r reqs/default.txt > /dev/null
pip install -r reqs/dev.txt > /dev/null
echo -e "\r - Successfully installed dependencies."

chmod +x manage.py

find . -type f -name ".keep" | xargs rm
rm mkproject.sh
rm README.rst

echo -e "Done.\nYour project is located in $(pwd)"
