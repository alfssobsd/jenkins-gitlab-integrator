FROM python:3.5


VOLUME /opt/app/config

WORKDIR /opt/app
COPY . /opt/app

RUN pip install -r requirements.txt

ENTRYPOINT ["/opt/app/docker-entrypoint.sh"]

CMD ["server"]
