import logging
from server.core.models import RecordNotFound
from server.core.models.jenkins_groups import JenkinsGroupManager, JenkinsGroup
from server.core.models.jenkins_jobs import JenkinsJobManager, JenkinsJob

async def init_example_data(db_pool, db_tables, marker='init_example_data'):
    _jenkins_group_manager = JenkinsGroupManager(marker, db_pool, db_tables)
    _jenkins_job_manager = JenkinsJobManager(marker, db_pool, db_tables)

    for task_name in ['jgi_example_single_task', 'jgi_example_multi_task', 'jgi_example_tree_task']:
        try:
            await _jenkins_group_manager.find_by_name(name=task_name)
            logging.info('example task already exist')
            return 0
        except RecordNotFound as e:
            pass

    # jgi_example_single_task
    group = JenkinsGroup()
    group.name = "jgi_example_single_task"
    group.jobs_base_path = "http://jenkins.example.local/job/example/"
    group = await _jenkins_group_manager.create(group)

    job = JenkinsJob()
    job.name = 'single_job'
    job.jenkins_group_id = group.id
    job.gitlab_project_id = 8000

    job = await _jenkins_job_manager.create(job)

    # jgi_example_multi_task
    group = JenkinsGroup()
    group.name = "jgi_example_multi_task"
    group.jobs_base_path = "http://jenkins.example.local/job/example/"
    group = await _jenkins_group_manager.create(group)

    first_job = JenkinsJob()
    first_job.name = 'mulit_job_first'
    first_job.jenkins_group_id = group.id
    first_job.gitlab_project_id = 8001

    first_job = await _jenkins_job_manager.create(first_job)

    last_job = JenkinsJob()
    last_job.name = 'mulit_job_last'
    last_job.jenkins_group_id = group.id
    last_job.gitlab_project_id = 8002
    last_job.jenkins_job_perent_id = first_job.id

    last_job = await _jenkins_job_manager.create(last_job)

    # jgi_example_tree_task
    group = JenkinsGroup()
    group.name = "jgi_example_tree_task"
    group.jobs_base_path = "http://jenkins.example.local/job/example/"
    group = await _jenkins_group_manager.create(group)

    first_job = JenkinsJob()
    first_job.name = 'tree_first_second'
    first_job.jenkins_group_id = group.id
    first_job.gitlab_project_id = 8004

    first_job = await _jenkins_job_manager.create(first_job)

    second_job = JenkinsJob()
    second_job.name = 'tree_job_second'
    second_job.jenkins_group_id = group.id
    second_job.gitlab_project_id = 8005
    second_job.jenkins_job_perent_id = first_job.id

    second_job = await _jenkins_job_manager.create(second_job)

    gitlab_id_index = 8006
    for job_name in ['tree_job_end_1', 'tree_job_end_2', 'tree_job_end_3']:
        gitlab_id_index += 1
        job = JenkinsJob()
        job.name = job_name
        job.jenkins_group_id = group.id
        job.gitlab_project_id = gitlab_id_index
        job.jenkins_job_perent_id = second_job.id

        job = await _jenkins_job_manager.create(job)
