# APServer

APServer is the module from the APScavenge tool that acts as a centralized point for managing, gathering, and displaying WPA-Enterprise connections security statistics derived from the data seized by hardware agents running the APAgent module. The APServer module is also responsible for providing web views for administration members to verify and manage that data. Its backend was developed using the Django framework. When using Docker, this module should work on all Docker-supported operating systems. If you want to run this module without Docker, it should work on Windows, Ubuntu, and Kali Linux operating systems.

## Considerations when running the APServer module

To run the central server module on the correct server ip and on a specific port, you should replace the following {ip} and {port} placeholders accordingly:

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
		|	DJANGO_CSRF_TRUSTED_ORIGINS='http://127.0.0.1,http://0.0.0.0,http://{ip}:{port}'
		|
```

You should also be aware of some other environment variables, as they should be changed for your run. The most important ones are the ``DJANGO_DEBUG`` and ``DJANGO_SECRET_KEY`` variables. Both can be found within the ``approject/.env.local`` file of the APServer module directory, which is imported in ``approject/approject/settings.py``. Debug should always be set to False during production and the secret should also be updated as the current one is publicly available.

By default, the server is set to run with a simple SQLite database for testing and development reasonings. Nonetheless, heading to the ``approject/approject/settings.py`` file, you can go to the ``# Database`` section, comment out the SQLite database definition, and uncomment the PostgreSQL version to make use of this later database technology. You will also need to change the default Postgres settings, although if you are running using the provided Docker method, the container isolation should make it difficult for outsiders to communicate with the Postgres database.

## Docker Compose

Docker was used to provide an automated way to start the APServer module. Having Docker and Docker Compose installed in the system, you just need to run the ``docker_run.sh`` file to start the server. This is commended when running in production mode.

## Running manually

It is recommended to use a Python virtual environment when running this module manually. The venv can be created at the root directory ```"APScavenge/"```. This should be used during development.

With the virtual environment created and started, you just need to run the command ``python manage.py runserver 0.0.0.0:8000`` (be sure to be in the same directory as ``manage.py``) to start the server.

## Required Packages

The following Python packages are required to run the APServer module:

```
pip install django
pip install djangorestframework
pip install python-dotenv
pip install requests
pip install cryptography
pip install psycopg2
pip install bs4
pip install selenium
pip install lxml
pip install apscheduler
```