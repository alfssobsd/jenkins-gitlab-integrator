import pprint
import json
import asyncio
import aiohttp_security
from functools import partial
from aiohttp import web
from server.core.common import LoggingMixin
from server.core.models.delayed_tasks import DelayedTaskStatus
from server.core.models.jenkins_groups import JenkinsGroup
from server.core.json_encoders import CustomJSONEncoder
from server.core.security.policy import require_permission, Permission
from . import set_log_marker, create_delayed_manager, create_jenkins_group_manager

class AdminApiV1ConfigView(web.View, LoggingMixin):
    """
        Admin API Config v1
    """
    @set_log_marker
    @require_permission(Permission.ADMIN_UI)
    async def get(self):
        return web.json_response( { 'body': pprint.pformat(self.request.app['config'], indent=2, width=256) } )

class AdminApiV1DelayedTasksView(web.View, LoggingMixin):
    """
        Admin API List/Search DelayedTask v1
    """
    @set_log_marker
    @create_delayed_manager
    @require_permission(Permission.ADMIN_UI)
    async def get(self):
        form_data = self._parse_form_data(self.request.query)
        self._logging_debug(form_data)
        tasks = await self.delayed_task_manager.search(**form_data)
        return web.json_response(tasks, dumps=partial(json.dumps, cls=CustomJSONEncoder))


    def _parse_form_data(self, query):
        form_data = {
            'task_type' : 'GITLAB_MERGE_REQ',
            'group' : None,
            'job_name' : None,
            'branch' : None,
            'sha1' : None,
        }

        for key in query.keys():
            if key in form_data:
                if query[key]:
                    form_data[key] = query[key]

        return form_data

class AdminApiV1DelayedTaskDetailView(web.View, LoggingMixin):
    """
        Admin API edit DelayedTask v1
    """
    @set_log_marker
    @create_delayed_manager
    @require_permission(Permission.ADMIN_UI)
    async def get(self):
        task_id = self.request.match_info['id']
        task = await self.delayed_task_manager.get(task_id)
        return web.json_response(task, dumps=partial(json.dumps, cls=CustomJSONEncoder))


class AdminApiV1DelayedTaskChangeStatusView(web.View, LoggingMixin):
    """
        Admin API change status DelayedTask v1
    """
    @set_log_marker
    @create_delayed_manager
    @require_permission(Permission.ADMIN_UI)
    async def post(self):
        task_id = self.request.match_info['id']
        self._logging_debug(await self.request.json())

        data = await self.request.json()
        task_status = data['task_status']

        task = await self.delayed_task_manager.get(task_id)
        await self.delayed_task_manager.clear_attempts(task.id)
        await self.delayed_task_manager.set_status(task.id, DelayedTaskStatus[task_status.upper()])

        task = await self.delayed_task_manager.get(task_id)
        return web.json_response(task, dumps=partial(json.dumps, cls=CustomJSONEncoder))

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
            'name' : None,
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
    @require_permission(Permission.ADMIN_UI)
    async def delete(self):
        group = await self.jenkins_group_manager.delete(self.request.match_info['id'])
        return web.json_response({})
