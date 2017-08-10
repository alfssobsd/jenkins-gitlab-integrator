import aiohttp
import pytest

from server.core.clients.jenkins_client import JenkinsClient


async def test_jenkins_get_last_success_build_first(loop, fixture_fake_jenkins_server):
    server, port = await fixture_fake_jenkins_server
    jc = JenkinsClient("test_marker", "username", "password", loop=loop)
    job_base_path = "http://%s:%d/job/experements" % (server, port)
    job_name = "job_first"
    branch = "feature_4"
    repo_remote_url = "ssh://git@gitlab.example.local:2222/Sergey.Kravchuk/%s.git" % (job_name)
    build_info = await jc.get_last_success_build(job_base_path, job_name, branch, repo_remote_url)
    assert build_info.number == 1
    assert build_info.upsteram_build_number is None
    assert build_info.upsteram_project is None
    assert build_info.repo_remote_url == repo_remote_url
    assert build_info.sha1 == "0692f3f7f5f764a8a31b34ae768cb513ccc780b8"
    assert build_info.result == "SUCCESS"


async def test_jenkins_get_last_success_build_second(loop, fixture_fake_jenkins_server):
    server, port = await fixture_fake_jenkins_server
    jc = JenkinsClient("test_marker", "username", "password", loop=loop)
    job_base_path = "http://%s:%d/job/experements" % (server, port)
    job_name = "job_second"
    branch = "feature_4"
    repo_remote_url = "ssh://git@gitlab.example.local:2222/Sergey.Kravchuk/%s.git" % (job_name)
    build_info = await jc.get_last_success_build(job_base_path, job_name, branch, repo_remote_url)
    assert build_info.number == 1
    assert build_info.upsteram_build_number == 1
    assert build_info.upsteram_project == "experements/job_first/feature_4"
    assert build_info.repo_remote_url == repo_remote_url
    assert build_info.sha1 == "0692f3f7f5f764a8a31b34ae768cb513ccc780b8"
    assert build_info.result == "SUCCESS"

async def test_jenkins_get_exist_job(loop, fixture_fake_jenkins_server):
    server, port = await fixture_fake_jenkins_server
    jc = JenkinsClient("test_marker", "username", "password", loop=loop)
    job_base_path = "http://%s:%d/job/experements" % (server, port)
    job_name = "job_second"
    branch = "feature_4"
    repo_remote_url = "ssh://git@gitlab.example.local:2222/Sergey.Kravchuk/%s.git" % (job_name)
    build_info = await jc.job_exists(job_base_path, job_name, branch)

async def test_jenkins_get_not_exist_job(loop, fixture_fake_jenkins_server):
    with pytest.raises(aiohttp.client_exceptions.ClientResponseError) as e_info:
        server, port = await fixture_fake_jenkins_server
        jc = JenkinsClient("test_marker", "username", "password", loop=loop)
        job_base_path = "http://%s:%d/job/experements" % (server, port)
        job_name = "job_second"
        branch = "feature_5"
        repo_remote_url = "ssh://git@gitlab.example.local:2222/Sergey.Kravchuk/%s.git" % (job_name)
        build_info = await jc.job_exists(job_base_path, job_name, branch)

async def test_jenkins_get_forbidden_job(loop, fixture_fake_jenkins_server):
    with pytest.raises(aiohttp.client_exceptions.ClientResponseError) as e_info:
        server, port = await fixture_fake_jenkins_server
        jc = JenkinsClient("test_marker", "username", "wrongpassword", loop=loop)
        job_base_path = "http://%s:%d/job/experements" % (server, port)
        job_name = "job_second"
        branch = "feature_4"
        repo_remote_url = "ssh://git@gitlab.example.local:2222/Sergey.Kravchuk/%s.git" % (job_name)
        build_info = await jc.job_exists(job_base_path, job_name, branch)
