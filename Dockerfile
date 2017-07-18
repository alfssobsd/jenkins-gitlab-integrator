FROM python:3.5


VOLUME /opt/app/config

WORKDIR /opt/app
COPY . /opt/app

RUN pip install -r requirements.txt

CMD alembic upgrade head; python -m server.main -c /opt/app/config/server.yml
