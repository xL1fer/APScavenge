# Start the containers

sudo docker compose up -d

# Stop the containers

sudo docker compose down

# Check networks

sudo docker network ls

# Check volumes

sudo docker volume ls
sudo docker volume inspect apscavenge_static
sudo ls -la /var/lib/docker/volumes/apscavenge_static/_data

## Another way of checking data

sudo docker exec -it apscavenge-django_gunicorn-1 ls -la ../static

# Remove volume

sudo docker volume remove apscavenge_static

# Delete images

sudo docker images
sudo docker rmi [image_id]
sudo docker rmi apscavenge-django_gunicorn;sudo docker rmi apscavenge-nginx

# Delete volumes not being used

sudo docker volume prune

# Check current containers

sudo docker ps

# Check container erros

sudo docker logs [container_name] (apscavenge-django_gunicorn-1)

# Create django super user inside docker container

sudo docker exec -it apscavenge-django_gunicorn-1 python manage.py createsuperuser

# Shutdown and clear created container files and images

sudo docker compose down
sudo docker volume remove apscavenge_static
sudo docker rmi apscavenge-django_gunicorn;sudo docker rmi apscavenge-nginx