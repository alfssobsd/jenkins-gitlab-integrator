import hashlib
import random

import pytest

from server.core.clients.gitlab_client import GitLabPush
from server.core.models.delayed_tasks import DelayedTask, DelayedTaskStatus, DelayedTaskType
from server.core.services.gitlab_push_service import GitLabPushService


@pytest.fixture()
def gitlab_raw_push_job_exist():
    bits = random.getrandbits(128)
    h = hashlib.sha1()
    h.update("%032x".encode('utf-8') % bits)
    h.hexdigest()
    return {'ref': 'refs/heads/feature_4',
            'project_id': 2,
            'checkout_sha': h.hexdigest()}


@pytest.fixture()
def gitlab_raw_push_job_not_exist():
    bits = random.getrandbits(128)
    h = hashlib.sha1()
    h.update("%032x".encode('utf-8') % bits)
    h.hexdigest()
    return {'ref': 'refs/heads/feature_not_exist_999',
            'project_id': 2,
            'checkout_sha': h.hexdigest()}


@pytest.fixture()
async def fixture_gitlab_push_service(loop, request, fixture_db_pool, fixture_db_tables,
                                      fixture_workers_config, fixture_gitlab_config, fixture_jenkins_config):
    gitlab_config = await fixture_gitlab_config
    jenkins_config = await fixture_jenkins_config
    db_pool = fixture_db_pool
    log_marker = "test-marker"
    push_service = GitLabPushService(log_marker,
                                     db_pool,
                                     fixture_db_tables,
                                     jenkins_config,
                                     gitlab_config,
                                     fixture_workers_config,
                                     loop=loop)
    def resource_teardown():
        tasks = loop.run_until_complete(push_service._delayed_task_manager.search())
        for task in tasks:
            loop.run_until_complete(push_service._delayed_task_manager.delete(task.id))

    request.addfinalizer(resource_teardown)
    return push_service


async def test_proccessing_raw_push_if_job_exist(loop, gitlab_raw_push_job_exist, fixture_gitlab_push_service):
    group, job_name = "testproject", "testproject"
    push_service = await fixture_gitlab_push_service
    await push_service.exec_raw(group, job_name, gitlab_raw_push_job_exist)

    tasks = await push_service._delayed_task_manager.search(sha1=gitlab_raw_push_job_exist['checkout_sha'])

    assert len(tasks) == 0


async def test_proccessing_raw_push_if_job_not_exist(loop, gitlab_raw_push_job_not_exist, fixture_gitlab_push_service):
    group, job_name = "testproject", "testproject"
    push_service = await fixture_gitlab_push_service
    await push_service.exec_raw(group, job_name, gitlab_raw_push_job_not_exist)

    tasks = await push_service._delayed_task_manager.search(sha1=gitlab_raw_push_job_not_exist['checkout_sha'])
    # double search - problem with sql cache :(
    tasks = await push_service._delayed_task_manager.search(sha1=gitlab_raw_push_job_not_exist['checkout_sha'])

    assert tasks[0].task_status == DelayedTaskStatus.NEW.name
    assert tasks[0].task_type == DelayedTaskType.GITLAB_PUSH.name


async def test_exceeding_max_number_of_attempts(loop, gitlab_raw_push_job_not_exist, fixture_gitlab_push_service):
    group, job_name = "testproject", "testproject"
    push_service = await fixture_gitlab_push_service
    for i in range(push_service._workers_config['max_attempts'] + 4):
        await push_service.exec_raw(group, job_name, gitlab_raw_push_job_not_exist)

    tasks = await push_service._delayed_task_manager.search(sha1=gitlab_raw_push_job_not_exist['checkout_sha'])

    assert tasks[0].task_status == DelayedTaskStatus.CANCELED.name
    assert tasks[0].task_type == DelayedTaskType.GITLAB_PUSH.name
    assert tasks[0].counter_attempts == push_service._workers_config['max_attempts'] + 3


async def test_proccessing_push_from_db_if_job_exist(loop, gitlab_raw_push_job_exist, fixture_gitlab_push_service):
    group, job_name = "testproject", "testproject"
    push_service = await fixture_gitlab_push_service

    gitlab_push_obj = GitLabPush.from_push_data(gitlab_raw_push_job_exist)
    delayed_task = DelayedTask.make_push_task(group, job_name, gitlab_push_obj.sha1, gitlab_push_obj.branch)
    delayed_task = await push_service._delayed_task_manager.get_or_create(delayed_task)
    await push_service.exec(delayed_task)
    delayed_task = await push_service._delayed_task_manager.get_or_create(delayed_task)

    assert delayed_task.task_status == DelayedTaskStatus.SUCCESS.name
    assert delayed_task.branch == gitlab_push_obj.branch
    assert delayed_task.sha1 == gitlab_push_obj.sha1


async def test_proccessing_push_from_db_if_job_not_exist(loop, gitlab_raw_push_job_not_exist,
                                                         fixture_gitlab_push_service):
    group, job_name = "testproject", "testproject"
    push_service = await fixture_gitlab_push_service

    gitlab_push_obj = GitLabPush.from_push_data(gitlab_raw_push_job_not_exist)
    delayed_task = DelayedTask.make_push_task(group, job_name, gitlab_push_obj.sha1, gitlab_push_obj.branch)
    delayed_task = await push_service._delayed_task_manager.get_or_create(delayed_task)
    for i in range(5):
        await push_service.exec(delayed_task)
    delayed_task = await push_service._delayed_task_manager.get_or_create(delayed_task)

    assert delayed_task.task_status == DelayedTaskStatus.NEW.name
    assert delayed_task.counter_attempts == 5
    assert delayed_task.branch == gitlab_push_obj.branch
    assert delayed_task.sha1 == gitlab_push_obj.sha1
