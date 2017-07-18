import pytest
import json
import sqlalchemy as sa
from aiomysql.sa import create_engine
from tests.test_utils.fake_server.gitlab import FakeGitLabServer
from tests.test_utils.fake_server.jenkins import FakeJenkinsServer

@pytest.fixture()
async def fixture_fake_jenkins_server(loop, request):
    fake_server = FakeJenkinsServer(loop=loop)
    server, port = await fake_server.start()
    def resource_teardown():
        loop.run_until_complete(fake_server.stop())
    request.addfinalizer(resource_teardown)
    return server, port

@pytest.fixture()
async def fixture_fake_gitlab_server(loop, request):
    fake_server = FakeGitLabServer(loop=loop)
    server, port = await fake_server.start()
    def resource_teardown():
        loop.run_until_complete(fake_server.stop())
    request.addfinalizer(resource_teardown)
    return server, port

@pytest.fixture()
async def fixture_gitlab_config(fixture_fake_gitlab_server):
    server, port = await fixture_fake_gitlab_server
    return {
        'url': "http://%s:%d" % (server, port),
        'access_token': 'test_token'}

@pytest.fixture()
async def fixture_jenkins_config(fixture_fake_jenkins_server):
    server, port = await fixture_fake_jenkins_server
    return {
            'user_id': 'username',
            'api_token': 'password',
            'groups': {
                'testproject': {
                    'jobs_base_path': "http://%s:%d/job/experements" % (server, port),
                    'first_job': 'job_first',
                    'chains': {
                        'default': [
                            "job_first",
                            "job_second"
                        ]
                    }
                }
            }
        }

@pytest.fixture(scope="module")
def fixture_workers_config():
    return {
        'enable': True,
        'max_attempts': 10,
        'scan_timeout': 60
    }

@pytest.fixture(scope="module")
def fixture_db_tables():
    engine = sa.create_engine('mysql+pymysql://root:test@127.0.0.1:3307/test')
    conn = engine.connect()
    meta = sa.MetaData(conn)
    meta.reflect()
    conn.close()
    return meta.tables

@pytest.yield_fixture()
async def fixture_db_pool(request, loop):
    mysql_config = {
        'db': 'test',
        'host': '127.0.0.1',
        'user': 'root',
        'password': 'test',
        'port': 3307,
        'minsize': 2,
        'maxsize': 2,
    }
    engine = await create_engine(loop=loop, **mysql_config)
    def resource_teardown():
        engine.close()
        loop.run_until_complete(engine.wait_closed())
    request.addfinalizer(resource_teardown)
    return engine
