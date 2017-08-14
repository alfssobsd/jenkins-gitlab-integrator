import json
from functools import partial

from aiohttp import web

from server.core.common import LoggingMixin
from server.core.json_encoders import CustomJSONEncoder
from server.core.models.jenkins_jobs import JenkinsJob
from server.core.security.policy import require_permission, Permission
from server.core.views.api.mixins import WebHookApiMixin
from server.core.views import create_jenkins_group_manager, create_jenkins_job_manager, set_log_marker, \
    create_gitlab_client


class AdminApiV1JenkinsJobListView(web.View, LoggingMixin):
    """
        Admin API for find Jenkins Job by group
    """

    @set_log_marker
    @create_jenkins_job_manager
    @require_permission(Permission.ADMIN_UI)
    async def get(self):
        group_id = self.request.match_info['group_id']
        jobs = await self.jenkins_job_manager.find_by_group_id(int(group_id))
        return web.json_response(jobs, dumps=partial(json.dumps, cls=CustomJSONEncoder))


class AdminApiV1JenkinsJobView(web.View, LoggingMixin, WebHookApiMixin):
    """
        Admin API for mangmanet Jenkins Job
    """

    @set_log_marker
    @create_jenkins_job_manager
    @require_permission(Permission.ADMIN_UI)
    async def get(self):
        group_id = self.request.match_info['group_id']
        job_id = self.request.match_info['id']
        job = await self.jenkins_job_manager.get(job_id)
        return web.json_response(job, dumps=partial(json.dumps, cls=CustomJSONEncoder))

    @set_log_marker
    @create_jenkins_job_manager
    @require_permission(Permission.ADMIN_UI)
    async def post(self):
        group_id = self.request.match_info['group_id']
        json_data = await self.request.json()
        self._logging_debug(json_data)
        obj = JenkinsJob()
        obj.jenkins_group_id = group_id
        obj.name = json_data['name']
        try:
            obj.jenkins_job_perent_id = int(json_data['jenkins_job_perent_id'])
        except Exception as e:
            obj.jenkins_job_perent_id = None

        obj.gitlab_project_id = int(json_data['gitlab_project_id'])

        job = await self.jenkins_job_manager.create(obj)

        return web.json_response(job, dumps=partial(json.dumps, cls=CustomJSONEncoder))

    @set_log_marker
    @create_jenkins_job_manager
    @require_permission(Permission.ADMIN_UI)
    async def put(self):
        group_id = int(self.request.match_info['group_id'])
        job_id = int(self.request.match_info['id'])
        json_data = await self.request.json()
        self._logging_debug(json_data)
        obj = JenkinsJob()
        obj.id = job_id
        obj.jenkins_group_id = group_id
        obj.name = json_data['name']

        try:
            obj.jenkins_job_perent_id = int(json_data['jenkins_job_perent_id'])
        except Exception as e:
            obj.jenkins_job_perent_id = None

        obj.gitlab_project_id = int(json_data['gitlab_project_id'])

        self._logging_debug(obj.values)
        job = await self.jenkins_job_manager.update(obj)

        return web.json_response(job, dumps=partial(json.dumps, cls=CustomJSONEncoder))

    @set_log_marker
    @create_jenkins_job_manager
    @create_jenkins_group_manager
    @create_gitlab_client
    @require_permission(Permission.ADMIN_UI)
    async def delete(self):
        #delete webhook
        job = await self.jenkins_job_manager.get(self.request.match_info['id'])
        group = await self.jenkins_group_manager.get(job.jenkins_group_id)
        await self._delete_job_webhook(group, job, ignore_errors=True)

        #delete job
        job = await self.jenkins_job_manager.delete(self.request.match_info['id'])

        return web.json_response({})

class AdminApiV1JenkinsJobGitlabWebHookView(web.View, LoggingMixin, WebhookApiMixin):

    @set_log_marker
    @create_jenkins_job_manager
    @create_jenkins_group_manager
    @create_gitlab_client
    @require_permission(Permission.ADMIN_UI)
    async def delete(self):
        #delete webhook
        job = await self.jenkins_job_manager.get(self.request.match_info['id'])
        group = await self.jenkins_group_manager.get(job.jenkins_group_id)
        await self._delete_job_webhook(group, job, ignore_errors=True)

        return web.json_response({})

    @set_log_marker
    @create_jenkins_job_manager
    @create_jenkins_group_manager
    @create_gitlab_client
    @require_permission(Permission.ADMIN_UI)
    async def put(self):
        #delete webhook
        job = await self.jenkins_job_manager.get(self.request.match_info['id'])
        group = await self.jenkins_group_manager.get(job.jenkins_group_id)
        await self._delete_job_webhook(group, job, ignore_errors=True)
        await self._create_job_webhook(group, job)

        return web.json_response({})
