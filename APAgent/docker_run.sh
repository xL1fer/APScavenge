#!/bin/sh

sudo docker-compose down

sudo docker system prune -f

nmcli dev set wlan0 managed no

sudo docker-compose up --build