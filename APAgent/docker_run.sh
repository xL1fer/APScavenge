#!/bin/sh

source approject/.env.local
AP_IFACE="$AP_IFACE"

if [ -z "$AP_IFACE" ]; then
    echo "(Error) AP_IFACE not set in 'approject/.env.local'."
    exit 1
fi

sudo docker-compose down

sudo docker system prune -f

nmcli dev set $AP_IFACE managed no

sudo docker-compose up --build