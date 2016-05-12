#!/bin/sh

cd gt-python-sdk
sudo python setup.py install
cd ..
sudo pip install -r requirement.txt
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
