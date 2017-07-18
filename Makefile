dev_prepare:
	pip install -r requirements.txt
	docker-compose -p test -f docker-compose.yml up -d mysql

build_docker:
	find . -name __pycache__ -execdir rm -r {} +
	find . -name '*.pyc' -delete
	docker build -f Dockerfile  -t alfss/jenkins-gitlab-integrator:1.0.0 .

test:
	docker-compose -p test -f docker-compose.yml rm -fs mysql_test
	docker-compose -p test -f docker-compose.yml up -d mysql_test
	sleep 30
	alembic -n alembic_test upgrade head
	PYTHONPATH=. py.test -v
	docker-compose -p test -f docker-compose.yml rm -fs mysql_test
