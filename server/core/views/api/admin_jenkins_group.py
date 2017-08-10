import json
from functools import partial

from aiohttp import web

from server.core.common import LoggingMixin
from server.core.json_encoders import CustomJSONEncoder
from server.core.models.jenkins_groups import JenkinsGroup
from server.core.security.policy import require_permission, Permission
from server.core.views import create_jenkins_group_manager, set_log_marker, create_jenkins_job_manager, create_gitlab_client


class AdminApiV1JenkinsGroupSearchView(web.View, LoggingMixin):
    """
        Admin API for search Jenkins Group
    """

    @set_log_marker
    @create_jenkins_group_manager
    @require_permission(Permission.ADMIN_UI)
    async def get(self):
        form_data = self._parse_form_data(self.request.query)
        groups = await self.jenkins_group_manager.search(**form_data)
        return web.json_response(groups, dumps=partial(json.dumps, cls=CustomJSONEncoder))

    def _parse_form_data(self, query):
        form_data = {
            'name': None,
        }

        for key in query.keys():
            if key in form_data:
                if query[key]:
                    form_data[key] = query[key]

        return form_data


class AdminApiV1JenkinsGroupView(web.View, LoggingMixin):
    """
        Admin API for mangmanet Jenkins Group
    """

    @set_log_marker
    @create_jenkins_group_manager
    @require_permission(Permission.ADMIN_UI)
    async def get(self):
        group_id = self.request.match_info['id']
        group = await self.jenkins_group_manager.get(group_id)
        return web.json_response(group, dumps=partial(json.dumps, cls=CustomJSONEncoder))

    @set_log_marker
    @create_jenkins_group_manager
    @require_permission(Permission.ADMIN_UI)
    async def post(self):
        json_data = await self.request.json()
        self._logging_debug(json_data)
        obj = JenkinsGroup()
        obj.name = json_data['name']
        obj.jobs_base_path = json_data['jobs_base_path']
        group = await self.jenkins_group_manager.create(obj)

        return web.json_response(group, dumps=partial(json.dumps, cls=CustomJSONEncoder))

    @set_log_marker
    @create_jenkins_group_manager
    @require_permission(Permission.ADMIN_UI)
    async def put(self):
        json_data = await self.request.json()
        self._logging_debug(json_data)
        obj = JenkinsGroup()
        obj.id = self.request.match_info['id']
        obj.name = json_data['name']
        obj.jobs_base_path = json_data['jobs_base_path']

        await self.jenkins_group_manager.update(obj)

        group = await self.jenkins_group_manager.get(obj.id)
        return web.json_response(group, dumps=partial(json.dumps, cls=CustomJSONEncoder))

    @set_log_marker
    @create_jenkins_group_manager
    @create_jenkins_job_manager
    @require_permission(Permission.ADMIN_UI)
    async def delete(self):
        jobs = await  self.jenkins_job_manager.find_by_group_id(int(self.request.match_info['id']))
        for job in jobs:
            await self.jenkins_job_manager.delete(job.id)

        group = await self.jenkins_group_manager.delete(self.request.match_info['id'])
        return web.json_response({})


class AdminApiV1JenkinsGroupGitlabWebHooksView(web.View, LoggingMixin):
    """ Manage gitlab webhooks"""

    @set_log_marker
    @create_jenkins_group_manager
    @create_jenkins_job_manager
    @create_gitlab_client
    @require_permission(Permission.ADMIN_UI)
    async def put(self):
        """
            update webhooks
        """
        group = await self.jenkins_group_manager.get(self.request.match_info['id'])
        jobs = await self.jenkins_job_manager.find_by_group_id(int(self.request.match_info['id']))
        for job in jobs:
            hook_url = self._gen_hook_url(group, job)
            hooks = await self.gitlab_client.get_webhooks(job.gitlab_project_id)
            for hook in hooks:
                if not hook is None and hook.url == hook_url:
                    await self.gitlab_client.delete_webhook(job.gitlab_project_id, hook.id)
            await self.gitlab_client.create_webhook(job.gitlab_project_id, hook_url, self.request.app['config']['gitlab_webhook_token'])

        return web.json_response({'message': 'Update GitLab webhooks'})


    def _gen_hook_url(self, group, job):
        return "%s/gitlab/group/%s/job/%s" % (self.request.app['config']['server_url'], group.name, job.name)
