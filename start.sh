#!/bin/bash

#pip install -r /mentisparcment_docker/annotator_tool/requirements.txt
declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /mentisparchment_docker/container.env
cp /mentisparchment_docker/annotator_tool/annotate-cron /etc/cron.d/annotate-cron
chmod 0644 /etc/cron.d/annotate-cron
crontab /etc/cron.d/annotate-cron
touch /var/log/cron.log

service cron start

python manage.py runserver 0.0.0.0:80
