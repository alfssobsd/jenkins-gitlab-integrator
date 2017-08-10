from aiohttp import web

from server.core.common import LoggingMixin
from server.core.security.policy import auth_by_gitlab_token
from server.core.services.gitlab_merge_service import GitLabMergeService
from server.core.services.gitlab_push_service import GitLabPushService
from . import set_log_marker


class GitLabWebhookView(web.View, LoggingMixin):
    """
        GitLab webhook entrypoint
    """

    @auth_by_gitlab_token
    @set_log_marker
    async def post(self):
        request = self.request
        group = request.match_info['group']
        job_name = request.match_info['job_name']

        data = await request.json()
        if data['object_kind'] == 'push':
            self._logging_info("Push request")
            self._logging_debug("data:" + str(data))
            push_service = GitLabPushService(self._marker,
                                             request.app['db_pool'],
                                             request.app['sa_tables'],
                                             request.app['config']['jenkins'],
                                             request.app['config']['gitlab'],
                                             request.app['config']['workers'])

            await push_service.exec_raw(group, job_name, data)
        if data['object_kind'] == 'merge_request':
            self._logging_info("Merge request")
            self._logging_debug("data:" + str(data))
            merge_service = GitLabMergeService(self._marker,
                                               request.app['db_pool'],
                                               request.app['sa_tables'],
                                               request.app['config']['jenkins'],
                                               request.app['config']['gitlab'],
                                               request.app['config']['workers'])

            await merge_service.exec_raw(group, job_name, data)
        text = "OK"
        return web.Response(text=text)
