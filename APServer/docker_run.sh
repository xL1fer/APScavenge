#!/bin/sh

sudo docker-compose down

sudo docker system prune -f

sudo docker-compose up --build