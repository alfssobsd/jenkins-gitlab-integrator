from aiohttp.client_exceptions import ClientResponseError, ClientConnectorError

from server.core.common import LoggingMixin
from server.core.models.delayed_tasks import DelayedTaskManager, DelayedTaskStatus, DelayedTask, RecordNotFound
from server.core.clients.jenkins_client import JenkinsClient
from server.core.clients.gitlab_client import GitLabClient, GitLabMergeState, GitLabMerge


class GitLabMergeService(LoggingMixin):
    """
    Processing merge message from gitlab

    """

    def __init__(self, marker, db, db_tables, jenkins_config, gitlab_config, workers_config, loop=None):
        """
        Args:
            marker - uuid marker for flow
            db - db pool sqlalchemy
            db_tables - tables sqlalchemy
            jenkins_config - config jenkins
            gitlab_config - gitlab_config
            loop - asyncio loop, if None we get from MainThread
        """
        self._loop = loop
        self._marker = marker  # for logs
        self._jenkins_config = jenkins_config
        self._gitlab_config = gitlab_config
        self._workers_config = workers_config
        self._delayed_task_manager = DelayedTaskManager(self._marker, db, db_tables)
        self._jenkins_client = JenkinsClient(self._marker,
                                             jenkins_config['user_id'],
                                             jenkins_config['api_token'],
                                             loop=self._loop)
        self._gitlab_client = GitLabClient(self._marker,
                                           self._gitlab_config['url'],
                                           self._gitlab_config['access_token'],
                                           loop=self._loop)

    async def exec_raw(self, group, job_name, gitlab_raw_merge_data):
        """
        (raw data) Check merge request.

        Checking all jobs in Jenkins if all jobs in group have status success, MR request will be approved.
        If least one "job" in group continue running, created delayed task for check MR.

        Args:
            group - Jenkins apps group in jenkins_config
            job_name - Name of job in jenkins apps group
            gitlab_raw_merge_data - raw merge data from gitlab
        """
        merge_obj = GitLabMerge.from_raw_data(gitlab_raw_merge_data)
        self._logging_info(merge_obj)

        if merge_obj.state.value < GitLabMergeState.MERGED.value:
            delayed_task = DelayedTask.make_merge_task(group, job_name,
                                                       merge_obj.sha1, merge_obj.source_branch,
                                                       merge_obj.project_id, merge_obj.merge_id)
            await self.exec(delayed_task)
        else:
            self._logging_info("Skip %s" % merge_obj)

    async def exec(self, delayed_task):
        """
        (prepared data) Check merge request.

        Checking all jobs in Jenkins if all jobs in group have status success, MR request will be approved.
        If least one "job" in group continue running, created delayed task for check MR.

        Args:
            delayed_task - DelayedTask obje
        """
        self._logging_debug(delayed_task)
        if await self._is_relevance_task(delayed_task):
            build_status = await self._is_success_build(delayed_task)
            if build_status:
                await self._delayed_task_done(delayed_task)
            else:
                await self._delayed_task(delayed_task)
        else:
            await self._delayed_task_cancel(delayed_task)

    async def _is_relevance_task(self, delayed_task):
        """
        Task validation

        Valid task(if all option is true):
            - delayed task sha1 eq merge requst sha1
            - merge request not closed or merged

        Return:
            True - Valid
            False - Invalid
        """
        merge_req = await self._gitlab_client.get_merge_request(delayed_task.gitlab_project_id,
                                                                delayed_task.gitlab_merge_id)
        self._logging_debug(merge_req)
        if merge_req.sha1 != delayed_task.sha1 or merge_req.state.value >= GitLabMergeState.MERGED.value:
            await self._delayed_task_cancel(delayed_task)
            return False

        return True

    async def _is_success_build(self, delayed_task):
        """
        Check build

        successful(if all option is true):
            - all job exist
            - all last success build is correct flow (job1 -> job2 -> jobN)
            - all job have status SUCCESS
            - sha1 from delayed_task eq sha1 from last success build info

        Args:
            delayed_task - DelayedTask obj

        Return:
            True - successful build
            False - failure build
        """
        self._logging_info("check build %s" % delayed_task)
        ssh_url_to_repo = await self._gitlab_client.get_ssh_url_to_repo(delayed_task.gitlab_project_id)
        prev_build_info = None
        # check build flow
        try:
            for chain in self._get_chains_from_group(delayed_task.group):
                for job_name in self._get_jobs_from_chains(delayed_task.group, chain):
                    repo_remote_url = None

                    # if set repo for job_name from merge
                    if delayed_task.job_name == job_name:
                        repo_remote_url = ssh_url_to_repo

                    # get info about last succes build
                    build_info = await self._jenkins_client.get_last_success_build(
                        self._jenkins_base_path(delayed_task.group),
                        job_name,
                        delayed_task.branch,
                        repo_remote_url)
                    self._logging_debug(build_info)

                    # failure build if sha1 from mege does not match
                    if delayed_task.job_name == job_name:
                        if not build_info.sha1 == delayed_task.sha1:
                            return False

                    # failure build if not correct flow
                    if not prev_build_info is None:
                        if not build_info.upsteram_build_number == prev_build_info.number:
                            return False

                    # failure build if result not SUCCESS
                    if not build_info.result == "SUCCESS":
                        return False

                    prev_build_info = build_info
        except (ClientResponseError) as e:
            self._logging_debug(e)
            return False
        except (ClientConnectorError) as e:
            self._logging_error(e)
            return False

        return True

    async def _gitlab_create_or_update_comment(self, delayed_task, message):
        """
        Create or Update comment in merge request

        Args:
            delayed_task - DelayedTask obj
            message - text message

        Return:
            Int - merge_comment_id
        """
        if delayed_task.gitlab_merge_comment_id is None:
            return await self._gitlab_client.create_merge_comment(delayed_task.gitlab_project_id,
                                                                  delayed_task.gitlab_merge_id,
                                                                  message)

        return await self._gitlab_client.update_merge_comment(delayed_task.gitlab_project_id,
                                                              delayed_task.gitlab_merge_id,
                                                              delayed_task.gitlab_merge_comment_id,
                                                              message)

    async def _delayed_task(self, delayed_task):
        """
        Create DelayedTask
        """
        delayed_task = await self._delayed_task_manager.get_or_create(delayed_task)

        # hack for reopen merge
        await self._delayed_task_manager.set_status_new(delayed_task.id)
        delayed_task.task_status = DelayedTaskStatus.NEW

        # create first comment or update existing
        delayed_task.gitlab_merge_comment_id = await self._gitlab_create_or_update_comment(delayed_task,
                                                                                           '(🍋) WAIT STATUS sha:%s' % delayed_task.sha1)
        await self._delayed_task_manager.set_gitlab_merge_comment_id(delayed_task.id,
                                                                     delayed_task.gitlab_merge_comment_id)
        self._logging_info("delayed_task was created %s" % (delayed_task))

        # increment attempts
        await self._delayed_task_manager.increment_attempts(delayed_task.id)

        # if the number of attempts is exceeded, cancel the task
        if delayed_task.counter_attempts > self._workers_config['max_attempts']:
            await self._delayed_task_cancel(delayed_task)

    async def _delayed_task_cancel(self, delayed_task):
        """
        Mark DelayedTask is CANCELED
        """
        self._logging_info("cancel task %s" % delayed_task)
        delayed_task = await self._delayed_task_manager.get_or_create(delayed_task)
        delayed_task.task_status = DelayedTaskStatus.CANCELED

        delayed_task.gitlab_merge_comment_id = await self._gitlab_create_or_update_comment(delayed_task,
                                                                                           '(⛔) CANCELED sha:%s' % delayed_task.sha1)
        try:
            await self._delayed_task_manager.set_gitlab_merge_comment_id(delayed_task.id,
                                                                         delayed_task.gitlab_merge_comment_id)
            await self._delayed_task_manager.set_status_canceled(delayed_task.id)
        except RecordNotFound as e:
            pass
        except Exception as e:
            self._logging_error(e)

    async def _delayed_task_done(self, delayed_task):
        """
        Mark DelayedTask is SUCCESS
        """
        self._logging_info("done task %s" % delayed_task)
        delayed_task = await self._delayed_task_manager.get_or_create(delayed_task)
        delayed_task.task_status = DelayedTaskStatus.SUCCESS
        delayed_task.gitlab_merge_comment_id = await self._gitlab_create_or_update_comment(delayed_task,
                                                                                           '(🍏) SUCCESS sha:%s' % delayed_task.sha1)
        try:
            await self._delayed_task_manager.set_gitlab_merge_comment_id(delayed_task.id,
                                                                         delayed_task.gitlab_merge_comment_id)
            await self._delayed_task_manager.set_status_success(delayed_task.id)
        except RecordNotFound as e:
            pass
        except Exception as e:
            self._logging_error(e)

    def _get_chains_from_group(self, group):
        """
        Get chains from group
        """
        return self._jenkins_config['groups'][group]['chains'].keys()

    def _get_jobs_from_chains(self, group, chain):
        """
        Get jobs from  chains
        """
        return self._jenkins_config['groups'][group]['chains'][chain]

    def _get_first_job_from_group(self, group):
        """
        Get first job from jenkins group
        """
        return self._jenkins_config['groups'][group]['first_job']

    def _jenkins_base_path(self, group):
        """
        Get jobs_base_path from jenkins group
        """
        return self._jenkins_config['groups'][group]['jobs_base_path']
