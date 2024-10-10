# Installing Docker

## Setting up Docker's apt repository

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

## Installing the Docker packages

### To install the latest version, run:

```
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## Verifying that the Docker Engine installation is successful by running the hello-world image

```
sudo docker run hello-world
```

## Adding user to Docker group, removes the need of invoking Docker commands with sudo

```
sudo usermod -aG docker $USER
```

## Removing user from Docker group

```
sudo gpasswd --delete $USER docker
```

### Ubuntu references
- https://docs.docker.com/engine/install/ubuntu/

### Kali references
- https://malfunction-grinds.medium.com/how-to-install-docker-and-docker-compose-on-kali-linux-2ecd69c67ee9

- https://www.kali.org/docs/containers/installing-docker-on-kali/

# Docker commands

|Type|Command        |Description                    |
|-|---------------|-------------------------------|
|**Building**|||
||sudo docker compose build|`build Docker Compose file containers`|
||sudo docker compose up|`run Docker Compose file containers`|
||sudo docker compose up -d|`run Docker Compose file containers in detatch mode (background)`|
||sudo docker compose up --build -d|`run Docker Compose file containers in detatch mode (background) and rebuild containers if already created`|
||sudo docker compose down|`shutdown Docker Compose file containers`|
|**Containers**|||
||sudo docker ps|`check containers list`|
||sudo docker container ls|`check containers list (another way)`|
||sudo docker stop [container_name]|`stop single container`|
||sudo docker logs [container_name]|`check container errors`|
|**Networks**|||
||sudo docker network ls|`check networks list`|
|**Volumes**|||
||sudo docker volume ls|`check volumes list`|
||sudo docker volume inspect [volume_name]|`inspect a certain volume`|
||sudo ls -la /var/lib/docker/volumes/[volume_name]/_data|`check volume data`|
||sudo docker exec -it [container_name] ls -la ../static|`another way of checking volume data`|
||sudo docker volume remove [volume_name]|`delete a certain volume`|
||sudo docker volume prune|`delete volumes not being used`|
|**Images**|||
||sudo docker images|`check images list`|
||sudo docker rmi [image_id]|`delete a certain image`|
||sudo docker rmi [image_id];sudo docker rmi [image_id]|`delete multiple images`|
|**Misc**|||
||sudo docker exec -it [container_name] python manage.py createsuperuser|`create Django superuser inside a container`|
||sudo docker system prune|`delete stopped containers, networks, images and build cache`|
||sudo docker system prune -af --volumes|`same as above, but remove dangling resources as well (-a), don't ask for permission (-f) and also include volumes (--volumes)`|


## Sample set of commans to shutdown and clear Docker Compose containers' files and images

```
sudo docker compose down
sudo docker volume remove [volume_name]
sudo docker rmi [image_id]
```

### Commands references
- https://www.hostinger.com/tutorials/docker-remove-all-images-tutorial/
- https://stackoverflow.com/questions/54290925/how-do-i-look-at-whats-cached-by-docker