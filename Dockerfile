FROM python:3.10.12

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./approject /dockerapp

WORKDIR /dockerapp

COPY ./entrypoint.sh /
ENTRYPOINT [ "sh", "/entrypoint.sh" ]