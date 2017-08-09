# jenkins-gitlab-integrator

Server for integration GitLab CE with Jenkins (in last version GitLab (9.x) integration with jenkins enable only in EE version).

Server works only with multibranch pipeline jobs (maybe i will implement non-multibranch pipeline)

How it work:
* every  push starts build in jenkins (if the branch does not already exist, then the server will try to start the job until it reaches the limit of attempts or build starts.)
* for each merge request server checks the build and write comment about status

Menu:

* [Usage](#usage)
  * [Install requirements libs](#usage_install_libs)
  * [Configure database schema](#usage_config_db)
  * [Configure server](#usage_config_server)
  * [Configure integration with GitLab (webhooks)](#usage_gitlab_integration)
  * [Example Gitlab webhook](#usage_gitlab_webhook)
  * [Exec server](#usage_exec_server)
  * [Admin UI](#usage_admin_ui)
  * [App stats](#usage_stats)
* [Development](#development)
  * [Prepare dev machine](#development_prepare_dev)
  * [Prepare DB](#development_db)
  * [Libs](#development_libs)
  * [GitLab webhook processing](#development_gitlab_webhook)


## <a name="usage"></a> Usage

### <a name="usage_install_libs"></a> Install requirements libs
```
pip install -r requirements.txt
```

### <a name="usage_config_db"></a> Configure database schema

Edit alembic.ini , set sqlalchemy.url for connect database

Run migrations `alembic upgrade head`

```
vim alembic.ini
alembic upgrade head
```

### <a name="usage_config_server"></a> Configure server

config:
```
host: 0.0.0.0 # listen address
port: 8000 # listen port
log_level: INFO # log level

server_url: http://jenkins-gitlab-integrator.example.local:8000 #server url for gitlab webhooks (need for auto create webhooks)
gitlab_webhook_token: adEleRYsiViB1_34 #token for auth gitlab webhooks (Secret Token, Private-Token header)

#generate secret
#from cryptography.fernet import Fernet
#Fernet.generate_key()
session_secret: N5I6xGINvJ6RigIwd_SX7nHM4J7zYc6ONx6MGH3F__o= # salt for cookies
#user list
users:
  - username: root
    password: root
    permission: [ADMIN_UI]

#mysql connection, same as alembic.ini
mysql:
  db: jenkins_integrator
  host: 127.0.0.1
  user: root
  password: test
  port: 3306
  minsize: 5
  maxsize: 5

#gitlab api config
gitlab:
  url: https://gitlab.example.local #gitlab url
  access_token: adEleRYsiViB #gitlab user api token (look to gitlab docs)

#background workers config
workers:
  enable: yes #enable or disable run workers
  max_attempts: 1400 # how many try for do task
  scan_timeout: 60 # period between task run

jenkins: #settings for jenkins
  user_id: sergei.kravchuk #jenkins user
  api_token: 2342b01c03caaa0465d144e310893ba9 # jenkins api token
```

### <a name="usage_gitlab_integration"></a> Configure integration with GitLab (webhooks)

All flows in jenkins combined in groups. if all `jobs` in group is success, `merge` will be marked is as successful

Examples wokring flows:

![simple build (pipeline multibranch)](docs/images/jenkins-integrator-config-simple.png)

![star build (pipeline multibranch)](docs/images/jenkins-integrator-config-star.png)

Go to http://server:port/ui/jenkins-groups for configure.


### <a name="usage_gitlab_webhook"></a> Example Gitlab webhook

![docs/images/gitlab-webhook-settings.png](docs/images/gitlab-webhook-settings.png)


### <a name="usage_exec_server"></a> Exec server

Copy config to anower dirs and modify
```
cp config/alembic.yml /opt/jenkins-gitlab-integrator/config/
cp config/server.yml /opt/jenkins-gitlab-integrator/config/
```

Run migrations
```
docker run --rm -v /opt/jenkins-gitlab-integrator/config:/opt/app/config -it alfss/jenkins-gitlab-integrator:latest migrate
```

Start server
```
docker run -d -v /opt/jenkins-gitlab-integrator/config:/opt/app/config alfss/jenkins-gitlab-integrator:latest
```

Or you can make docker image with your config in /opt/app/config

### <a name="usage_admin_ui"></a> Admin UI

Admin UI provide:
 * management for delayed tasks
 * show current config & version
 * manage jenkins groups (webhooks)

```
Go to http://server:port/
```

### <a name="usage_stats"></a> App stats

`http://server:port/api/v1/stats` return json with stats.

```
{
    "coroutines_run": 2, # current execute coroutines
    "task_in_queue": 0, # count task with status new
    "app_version": "1.0.0"
}
```

## <a name="development"></a> Development

### <a name="development_prepare_dev"></a>  Prepared dev machine
```
apt-get install -y python3-dev python3 python3-venv
#init sandbox
python3 -m venv ~/py-sandbox/py3/server-jenkins-notify-py3
#use sandbox
source ~/py-sandbox/py3/server-jenkins-notify-py3/bin/activate
#install requirements
pip install -r requirements.txt
```

### <a name="development_db"></a> Prepare DB
```
#create database
create database jenkins_integrator DEFAULT CHARACTER SET utf8;

vim alembic.ini
alembic -c config/alembic.ini upgrade head
```

### Build UI
```
cd angular-admin-ui
ng build -d /static/
```

### Run server
```
python -m server.main -c /path/to/config/server.yml
```

### Run test
```
make test
```

### <a name="development_libs"></a> Libs

#### Python Libs
* [https://github.com/aio-libs/aiohttp]
* [https://github.com/aio-libs/aiomysql]
* [http://alembic.zzzcomputing.com/en/latest/]
* [https://pypi.python.org/pypi/aiodns]
* [https://www.sqlalchemy.org/]
* [https://pypi.python.org/pypi/trafaret]
* [http://jinja.pocoo.org/docs/2.9/]
* [https://github.com/aio-libs/aiohttp-security]
* [https://github.com/aio-libs/aiohttp-session]
* [https://pypi.python.org/pypi/cryptography]

#### UI Libs
* [https://angular.io/]

### <a name="development_gitlab_webhook"></a> Gitlab webhook processing

#### Push processing

![push processing](docs/images/jenkins-integrator-gitlab-webhook-push.jpg)

#### Mege processing

![merge processing](docs/images/jenkins-integrator-gitlab-webhook-merge.jpg)


