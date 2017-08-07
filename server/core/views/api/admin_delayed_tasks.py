import json
from functools import partial

from aiohttp import web

from server.core.common import LoggingMixin
from server.core.json_encoders import CustomJSONEncoder
from server.core.models.delayed_tasks import DelayedTaskStatus
from server.core.security.policy import require_permission, Permission
from server.core.views import create_delayed_manager, set_log_marker


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
