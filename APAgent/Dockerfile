FROM python:3.10.12

RUN apt-get update && apt-get install -y \
    network-manager \
    iproute2 \
    libnl-genl-3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./approject /dockerapp

WORKDIR /dockerapp

COPY ./entrypoint.sh /
ENTRYPOINT [ "sh", "/entrypoint.sh" ]