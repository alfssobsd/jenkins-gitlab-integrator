VERSION := $(shell cat server/main.py | grep -i "SERVER_VERSION =" | cut -d'=' -f2 | tr -d '" \n')

dev_prepare:
	pip install -r requirements.txt
	docker-compose -p dev -f docker-compose.yml up -d mysql
	sleep 30
	mysql -u root -h 127.0.0.1 -P 3306 -e "create database if not exists jenkins_integrator";
	alembic -c config/alembic.ini upgrade head

dev_server:
	docker-compose -p dev -f docker-compose.yml run --rm server migrate
	docker-compose -p dev -f docker-compose.yml up -d server

build_docker:
	find . -name __pycache__ -execdir rm -rf {} + 2>/dev/null
	find . -name '*.pyc' -delete 2>/dev/null
	docker build -f Dockerfile  -t alfss/jenkins-gitlab-integrator:latest .

build_docker_release:
	find . -name __pycache__ -execdir rm -rf {} + 2>/dev/null
	find . -name '*.pyc' -delete 2>/dev/null
	docker build -f Dockerfile  -t alfss/jenkins-gitlab-integrator:latest .
	docker build -f Dockerfile  -t alfss/jenkins-gitlab-integrator:${VERSION} .

push_docker_release:
	docker push alfss/jenkins-gitlab-integrator:latest
	docker push alfss/jenkins-gitlab-integrator:${VERSION}

test:
	mysql -u root -h 127.0.0.1 -P 3306 -e "drop database if exists test_jenkins_integrator";
	mysql -u root -h 127.0.0.1 -P 3306 -e "create database if not exists test_jenkins_integrator DEFAULT CHARACTER SET utf8;"
	alembic -n alembic_test -c config/alembic.ini upgrade head
	PYTHONPATH=. py.test -v
