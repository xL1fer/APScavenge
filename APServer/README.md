# APScavenge

## Python Virtual Environment

It is recommended to use a python virtual environment when running this project in development. The venv can be created at the root directory ```"APScavenge/"```.

When running in production mode, using docker is commended, for which the required files are already present in the project.

### Windows python venv

Download and install python:
```
https://www.python.org/downloads/
```

Create venv:
```
$ cd /APScavenge
$ python -m venv venv
```

Activate/deactivate venv:
```
venv\Scripts\activate.bat
venv\Scripts\deactivate.bat
```

### Linux python venv

Update packages:
```
$ sudo apt-get update
$ sudo apt-get -y upgrade
```

Install python3:
```
$ python3 -V
$ sudo apt-get install -y python3-pip
```

Install venv:
```
$ sudo apt-get install -y python3-venv
```

Create venv:
```
$ cd /APScavenge
$ python -m venv venv
```

Activate/deactivate venv:
```
$ source venv/bin/activate
$ deactivate
```

## Required Packages

Once the venv is activated, the following packages are required to run the project:

- pip install django
- pip install djangorestframework
- pip install python-dotenv
- pip install requests
- pip install cryptography