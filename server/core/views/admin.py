import pprint
import asyncio
import aiohttp_jinja2
import aiohttp_security
from aiohttp import web
from server.core.common import LoggingMixin
from server.core.security.policy import require_permission, Permission
from server.core.models.delayed_tasks import DelayedTaskStatus
from . import set_log_marker, create_delayed_manager

class AdminIndexView(web.View, LoggingMixin):
    """
        Admin index page
    """
    @set_log_marker
    @aiohttp_jinja2.template('admin/index.html.j2')
    @require_permission(Permission.ADMIN_UI)
    async def get(self):
        return { 'config': pprint.pformat(self.request.app['config'], indent=2, width=256)}

class AdminDelayedTasksEditView(web.View, LoggingMixin):
    """
        Show DelayedTask by status
    """
    @set_log_marker
    @create_delayed_manager
    @aiohttp_jinja2.template('admin/delayed_task/edit.html.j2')
    @require_permission(Permission.ADMIN_UI)
    async def get(self):
        task_id = self.request.match_info['id']
        delayed_task = await self.delayed_task_manager.get(task_id)
        return { 'task': delayed_task }

class AdminDelayedTasksChangeStatusView(web.View, LoggingMixin):
    """
        Change DelayedTask status
    """
    @set_log_marker
    @create_delayed_manager
    @require_permission(Permission.ADMIN_UI)
    async def post(self):
        task_id = self.request.match_info['id']
        data = await self.request.post()
        task_status = data['task_status']

        admin_delayed_task_list_url = self.request.app.router['admin_delayed_task_edit'].url(parts={'id': task_id })

        delayed_tasks = await self.delayed_task_manager.get(task_id)
        await self.delayed_task_manager.clear_attempts(delayed_tasks.id)
        await self.delayed_task_manager.set_status(delayed_tasks.id, DelayedTaskStatus[task_status.upper()])

        return web.HTTPFound(admin_delayed_task_list_url)

class AdminDelayedTasksSearchView(web.View, LoggingMixin):
    """
        Search DelayedTask by task_type, group, job_name, branch, sha1
    """
    @set_log_marker
    @create_delayed_manager
    @aiohttp_jinja2.template('admin/delayed_task/search.html.j2')
    @require_permission(Permission.ADMIN_UI)
    async def get(self):
        form_data = self._parse_form_data(self.request.query)
        tasks = await self.delayed_task_manager.search(**form_data)
        return {'form_data': form_data, 'tasks': tasks }


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
                form_data[key] = query[key]

        return form_data
