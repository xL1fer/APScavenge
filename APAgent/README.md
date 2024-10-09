# APAgent

APAgent is the module from the APScavenge tool that acts as an agent responsible for seizing WPA-Enterprise connections data and sending this data to the central APServer module. Its backend was developed using the Flask framework. When using Docker, this module should work on all Docker-supported operating systems. If you want to run this module without Docker, it should work on Ubuntu and Kali Linux operating systems.

## Considerations for running the APAgent module

To run the agent module on the correct server ip and on a specific port, you should replace the following {ip} and {port} placeholders accordingly:

```
	docker-compose.yml
		|
		|  nginx:
		|	build: ./nginx
		|	volumes:
		|	  - static:/static
		|	ports:
		|	  - "{port}:{port}"
		|
	
	nginx/default.conf
		|
		|	server {
		|		listen {port};
		|
	
	approject/.env.local
		|
		|	AGENT_IP='{ip}:{port}'
		|
	
    entrypoint.sh
        |
        |	gunicorn --bind {ip}:8000 resolver:app #--log-level debug
        |
    
    nginx/default.conf
        |
        |	upstream flask {
        |		server {ip}:8000;
        |	}
        |
```

You also need to ensure the central server ip is set to the correct ip and port:

```
	approject/.env.local
		|
		|	CENTRAL_IP='{centeral_server_ip}:{centeral_server_port}'
		|
```

## Docker Compose

Docker was used to provide an automated way to start the APAgent module. Having Docker and Docker Compose installed in the system, you just need to run the ``docker_run.sh`` file to start the agent. This is commended when running in production mode.

## Running manually

It is recommended to use a python virtual environment when running this module manually. The venv can be created at the root directory ```"APScavenge/"```. This should be used during development.

With the virtual environment created and started, you just need to run the command ``sudo flask --app resolver run --host=0.0.0.0`` (be sure to be in the same directory as ``resolver.py``) to start the agent.

## Required Packages

The following python packages are required to run the APAgent module:

```
pip install python-dotenv
pip install requests
pip install cryptography
pip install apscheduler
pip install netifaces
pip install psutil
```