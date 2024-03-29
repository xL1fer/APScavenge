#!/bin/sh

pip install python-dotenv
pip install requests
pip install cryptography
pip install apscheduler
pip install netifaces
pip install psutil

make -C pymana/hostapd-mana/hostapd clean
make -C pymana/hostapd-mana/hostapd

gunicorn --bind 192.168.1.84:8000 resolver:app #--log-level debug