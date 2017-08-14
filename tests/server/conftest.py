import pytest
import sqlalchemy as sa
from aiomysql.sa import create_engine

from server.core.models.jenkins_groups import JenkinsGroupManager, JenkinsGroup
from server.core.models.jenkins_jobs import JenkinsJobManager, JenkinsJob
from tests.test_utils.fake_server.gitlab import FakeGitLabServer
from tests.test_utils.fake_server.jenkins import FakeJenkinsServer


@pytest.fixture()
async def fixture_fake_jenkins_server(loop, request, fixture_db_pool, fixture_db_tables):
    fake_server = FakeJenkinsServer(loop=loop)
    server, port = await fake_server.start()

    db_pool = fixture_db_pool
    log_marker = 'test-marker'
    jenkins_group_manager = JenkinsGroupManager(log_marker, db_pool, fixture_db_tables)
    jenkins_job_manager = JenkinsJobManager(log_marker, db_pool, fixture_db_tables)

    def resource_teardown():
        jenkins_group = loop.run_until_complete(jenkins_group_manager.find_by_name('testproject'))
        jenkins_jobs = loop.run_until_complete(jenkins_job_manager.find_by_group_id(jenkins_group.id))
        for job in jenkins_jobs:
            loop.run_until_complete(jenkins_job_manager.delete(job.id))
        loop.run_until_complete(jenkins_group_manager.delete(jenkins_group.id))
        loop.run_until_complete(fake_server.stop())

    request.addfinalizer(resource_teardown)

    # init db data
    # prepare jenkins group
    jenkins_group = JenkinsGroup()
    jenkins_group.name = "testproject"
    jenkins_group.jobs_base_path = "http://%s:%d/job/experements" % (server, port)
    jenkins_group = await jenkins_group_manager.create(jenkins_group)

    # prepare first jenkins jobs
    jenkins_job_f = JenkinsJob()
    jenkins_job_f.gitlab_project_id = 1
    jenkins_job_f.jenkins_group_id = jenkins_group.id
    jenkins_job_f.name = 'job_first'
    jenkins_job_f.jenkins_job_perent_id = None
    jenkins_job_f = await jenkins_job_manager.create(jenkins_job_f)

    # prepare second jenkins job

    jenkins_job_s = JenkinsJob()
    jenkins_job_s.gitlab_project_id = 1
    jenkins_job_s.jenkins_group_id = jenkins_group.id
    jenkins_job_s.name = 'job_second'
    jenkins_job_s.jenkins_job_perent_id = jenkins_job_f.id
    jenkins_job_s = await jenkins_job_manager.create(jenkins_job_s)

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
    engine = sa.create_engine('mysql+pymysql://root@127.0.0.1/test_jenkins_integrator')
    conn = engine.connect()
    meta = sa.MetaData(conn)
    meta.reflect()
    conn.close()
    return meta.tables


@pytest.yield_fixture()
def fixture_db_pool(request, loop):
    mysql_config = {
        'db': 'test_jenkins_integrator',
        'host': '127.0.0.1',
        'user': 'root',
        'port': 3306,
        'minsize': 2,
        'maxsize': 2,
    }
    engine = loop.run_until_complete(create_engine(loop=loop, **mysql_config))

    def resource_teardown():
        engine.close()
        loop.run_until_complete(engine.wait_closed())

    request.addfinalizer(resource_teardown)
    return engine
