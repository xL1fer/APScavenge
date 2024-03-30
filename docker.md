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

## 4. Adding user to docker group, removes the need of invoking docker commands with sudo

```
sudo usermod -aG docker $USER
```

## 5. Removing user from docker group

```
sudo gpasswd --delete $USER docker
```

#### Ubuntu references
[https://docs.docker.com/engine/install/ubuntu/]

#### Kali references
[https://malfunction-grinds.medium.com/how-to-install-docker-and-docker-compose-on-kali-linux-2ecd69c67ee9]
[https://www.kali.org/docs/containers/installing-docker-on-kali/]

# Start the containers

```
sudo docker compose up -d
sudo docker compose up --build -d # rebuild containers if already created
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
sudo docker volume inspect apserver_static
sudo ls -la /var/lib/docker/volumes/apserver_static/_data
```

## Another way of checking data

```
sudo docker exec -it apserver_django_gunicorn_1 ls -la ../static
```

# Remove volume

```
sudo docker volume remove apserver_static
```

# Delete images

```
sudo docker images
sudo docker rmi [image_id]
sudo docker rmi apserver_django_gunicorn;sudo docker rmi apserver_nginx
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
sudo docker logs [container_name] (apserver_django_gunicorn_1)
```

# Create django super user inside docker container

```
sudo docker exec -it apserver_django_gunicorn_1 python manage.py createsuperuser
```

# Shutdown and clear created container files and images

```
sudo docker compose down
sudo docker volume remove apserver_static
sudo docker rmi apserver_django_gunicorn;sudo docker rmi apserver_nginx
```