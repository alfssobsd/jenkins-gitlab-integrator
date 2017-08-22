import aiohttp
import pytest

from server.core.clients.jenkins_client import JenkinsClient

@pytest.fixture()
def jenkins_client(loop):
    jc = JenkinsClient("test_marker", "username", "password", loop=loop)
    return jc

@pytest.fixture()
def jenkins_wrong_client(loop):
    jc = JenkinsClient("test_marker", "username", "wrongpassword", loop=loop)
    return jc

async def test_jenkins_get_last_success_build_first(loop, fixture_fake_jenkins_server, jenkins_client):
    server, port = await fixture_fake_jenkins_server
    job_base_path = "http://%s:%d/job/experements" % (server, port)
    job_name = "job_first"
    branch = "feature_4"
    repo_remote_url = "ssh://git@gitlab.example.local:2222/Sergey.Kravchuk/%s.git" % (job_name)
    build_info = await jenkins_client.get_last_success_build(job_base_path, job_name, branch, repo_remote_url)
    assert build_info.number == 1
    assert build_info.upsteram_build_number is None
    assert build_info.upsteram_project is None
    assert build_info.repo_remote_url == repo_remote_url
    assert build_info.sha1 == "0692f3f7f5f764a8a31b34ae768cb513ccc780b8"
    assert build_info.result == "SUCCESS"


async def test_jenkins_get_last_success_build_second(loop, fixture_fake_jenkins_server, jenkins_client):
    server, port = await fixture_fake_jenkins_server
    job_base_path = "http://%s:%d/job/experements" % (server, port)
    job_name = "job_second"
    branch = "feature_4"
    repo_remote_url = "ssh://git@gitlab.example.local:2222/Sergey.Kravchuk/%s.git" % (job_name)
    build_info = await jenkins_client.get_last_success_build(job_base_path, job_name, branch, repo_remote_url)
    assert build_info.number == 1
    assert build_info.upsteram_build_number == 1
    assert build_info.upsteram_project == "experements/job_first/feature_4"
    assert build_info.repo_remote_url == repo_remote_url
    assert build_info.sha1 == "0692f3f7f5f764a8a31b34ae768cb513ccc780b8"
    assert build_info.result == "SUCCESS"

async def test_jenkins_get_exist_job(loop, fixture_fake_jenkins_server, jenkins_client):
    server, port = await fixture_fake_jenkins_server
    job_base_path = "http://%s:%d/job/experements" % (server, port)
    job_name = "job_second"
    branch = "feature_4"
    repo_remote_url = "ssh://git@gitlab.example.local:2222/Sergey.Kravchuk/%s.git" % (job_name)
    build_info = await jenkins_client.job_exists(job_base_path, job_name, branch)

async def test_jenkins_get_not_exist_job(loop, fixture_fake_jenkins_server, jenkins_client):
    with pytest.raises(aiohttp.client_exceptions.ClientResponseError) as e_info:
        server, port = await fixture_fake_jenkins_server
        job_base_path = "http://%s:%d/job/experements" % (server, port)
        job_name = "job_second"
        branch = "feature_5"
        repo_remote_url = "ssh://git@gitlab.example.local:2222/Sergey.Kravchuk/%s.git" % (job_name)
        build_info = await jenkins_client.job_exists(job_base_path, job_name, branch)

async def test_jenkins_get_forbidden_job(loop, fixture_fake_jenkins_server, jenkins_wrong_client):
    with pytest.raises(aiohttp.client_exceptions.ClientResponseError) as e_info:
        server, port = await fixture_fake_jenkins_server
        job_base_path = "http://%s:%d/job/experements" % (server, port)
        job_name = "job_second"
        branch = "feature_4"
        repo_remote_url = "ssh://git@gitlab.example.local:2222/Sergey.Kravchuk/%s.git" % (job_name)
        build_info = await jenkins_wrong_client.job_exists(job_base_path, job_name, branch)

async def test_jenkins_single_job_builds_numbers(loop, fixture_fake_jenkins_server, jenkins_client):
    server, port = await fixture_fake_jenkins_server
    job_base_path = "http://%s:%d" % (server, port)
    job_name = "job_second"
    branch = "feature_4"
    build_numbers = await jenkins_client.get_build_numbers(job_base_path, job_name, branch, is_multibranch=False)
    assert build_numbers == [19, 20, 21]

    job_name = "job_first"
    build_numbers = await jenkins_client.get_build_numbers(job_base_path, job_name, branch, is_multibranch=False)
    assert build_numbers == [19, 20, 21]

    with pytest.raises(aiohttp.client_exceptions.ClientResponseError) as e_info:
        job_name = "not_exist"
        build_numbers = await jenkins_client.get_build_numbers(job_base_path, job_name, branch, is_multibranch=False)

async def test_jenkins_pipline_job_builds_numbers(loop, fixture_fake_jenkins_server, jenkins_client):
    server, port = await fixture_fake_jenkins_server
    job_base_path = "http://%s:%d/job/experements" % (server, port)
    job_name = "job_second"
    branch = "feature_4"
    build_numbers = await jenkins_client.get_build_numbers(job_base_path, job_name, branch, is_multibranch=True)
    assert build_numbers == [19, 20, 21]
