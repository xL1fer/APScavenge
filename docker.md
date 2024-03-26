# Installing docker

## 1. Set up Docker's apt repository.

### Add Docker's official GPG key:

```
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

### Add the repository to Apt sources:

```
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

## 2. Install the Docker packages.

### To install the latest version, run:

```
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## 3. Verify that the Docker Engine installation is successful by running the hello-world image.

```
sudo docker run hello-world
```

[https://docs.docker.com/engine/install/ubuntu/]

# Start the containers

```
sudo docker compose up -d
```

# Stop the containers

```
sudo docker compose down
```

# Check networks

```
sudo docker network ls
```

# Check volumes

```
sudo docker volume ls
sudo docker volume inspect apscavenge_static
sudo ls -la /var/lib/docker/volumes/apscavenge_static/_data
```

## Another way of checking data

```
sudo docker exec -it apscavenge-django_gunicorn-1 ls -la ../static
```

# Remove volume

```
sudo docker volume remove apscavenge_static
```

# Delete images

```
sudo docker images
sudo docker rmi [image_id]
sudo docker rmi apscavenge-django_gunicorn;sudo docker rmi apscavenge-nginx
```

# Delete volumes not being used

```
sudo docker volume prune
```

# Check current containers

```
sudo docker ps
```

# Check container erros

```
sudo docker logs [container_name] (apscavenge-django_gunicorn-1)
```

# Create django super user inside docker container

```
sudo docker exec -it apscavenge-django_gunicorn-1 python manage.py createsuperuser
```

# Shutdown and clear created container files and images

```
sudo docker compose down
sudo docker volume remove apscavenge_static
sudo docker rmi apscavenge-django_gunicorn;sudo docker rmi apscavenge-nginx
```