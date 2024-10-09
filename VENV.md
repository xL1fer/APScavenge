# Installing python venv

## Windows python venv

Download and install python:
```
https://www.python.org/downloads/
```

Create venv:
```
cd /APScavenge
python -m venv venv
```

Activate/deactivate venv:
```
venv\Scripts\activate.bat
venv\Scripts\deactivate.bat
```

## Linux python venv

Update packages:
```
sudo apt-get update
sudo apt-get -y upgrade
```

Install python3:
```
python3 -V
sudo apt-get install -y python3-pip
```

Install venv:
```
sudo apt-get install -y python3-venv
```

Create venv:
```
cd /APScavenge
python -m venv venv
```

Activate/deactivate venv:
```
source venv/bin/activate
deactivate
```