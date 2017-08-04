import uuid
import asyncio

from server.core.common import LoggingMixin
from server.core.models.delayed_tasks import DelayedTaskManager, DelayedTaskType
from server.core.services.gitlab_push_service import GitLabPushService
from server.core.services.gitlab_merge_service import GitLabMergeService

class GitLabWorker(LoggingMixin):
    def __init__(self, app):
        self._marker = self._get_new_marker()
        self._db_pool = app['db_pool']
        self._db_tables = app['sa_tables']
        self._jenkins_config = app['config']['jenkins']
        self._gitlab_config = app['config']['gitlab']
        self._workers_config = app['config']['workers']

        self._push_service = GitLabPushService(self._marker,
                                                self._db_pool,
                                                self._db_tables,
                                                self._jenkins_config,
                                                self._gitlab_config,
                                                self._workers_config)
        self._merge_service = GitLabMergeService(self._marker,
                                                    self._db_pool,
                                                    self._db_tables,
                                                    self._jenkins_config,
                                                    self._gitlab_config,
                                                    self._workers_config)
        self._delayed_task_manager = DelayedTaskManager(self._marker, self._db_pool, self._db_tables)

    async def run(self):
        self._logging_info("Start (scan timeout:%d)" % (self._workers_config['scan_timeout']))
        while True:
            self._marker = self._get_new_marker()
            await asyncio.sleep(self._workers_config['scan_timeout'])
            self._logging_info("Start scan delayed tasks")
            try:
                tasks = await self._delayed_task_manager.get_by_status_new()
                self._logging_info("Found tasks:%d" % len(tasks))
                for task in tasks:
                    try:
                        if task.task_type == DelayedTaskType.GITLAB_MERGE_REQ.name:
                            await self._merge_service.exec(task)
                        if task.task_type == DelayedTaskType.GITLAB_PUSH.name:
                            await self._push_service.exec(task)
                    except Exception as e:
                        self._logging_exception(e)
            except Exception as e:
                self._logging_exception(e)

    async def stop(self):
        self._logging_info("Stop")


    def _get_new_marker(self):
        return "gitlab-worker-" + uuid.uuid4().hex
