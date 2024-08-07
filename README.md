# APScavenge

## NOTES

It is recommended to ensure all files are in unix format, the dos2unix package can be used:

```
sudo apt-get install dos2unix
```

Converting files within a root directory to unix format can be done with the following command:

```
find . -type f -exec dos2unix {} \;
```

## Running the central server module on a specific port (8080 for example)

### APServer

	docker-compose.yml
		|
		|  nginx:
		|	build: ./nginx
		|	volumes:
		|	  - static:/static
		|	ports:
		|	  - "8080:8080"
		|
	
	nginx/default.conf
		|
		|	server {
		|		listen 8080;
		|
	
	approject/.env.local
		|
		|	DJANGO_CSRF_TRUSTED_ORIGINS='http://127.0.0.1,http://0.0.0.0,http://192.168.1.79:8080'
		|

### APAgent

	approject/.env.local
		|
		|	CENTRAL_IP='192.168.1.79:8080'
		|
		
## Running the agent module on a specific port (8080 for example)

### APAgent

	docker-compose.yml
		|
		|  nginx:
		|	build: ./nginx
		|	volumes:
		|	  - static:/static
		|	ports:
		|	  - "8080:8080"
		|
	
	nginx/default.conf
		|
		|	server {
		|		listen 8080;
		|
	
	approject/.env.local
		|
		|	AGENT_IP='192.168.1.84:8080'
		|
	
	NOTE: ensure the agent ip is set to an interface with network connectivity
		
		entrypoint.sh
			|
			|	gunicorn --bind 192.168.1.84:8000 resolver:app #--log-level debug
			|
		
		nginx/default.conf
			|
			|	upstream flask {
			|		server 192.168.1.84:8000;
			|	}
			|