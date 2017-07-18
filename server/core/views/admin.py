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
        return { 'config': pprint.pformat(self.request.app['config'], indent=2, width=256),
                 'version' : self.request.app['version']}

class AdminDelayedTasksListView(web.View, LoggingMixin):
    """
        Show DelayedTask by status
    """
    @set_log_marker
    @create_delayed_manager
    @aiohttp_jinja2.template('admin/delayed_task/list.html.j2')
    @require_permission(Permission.ADMIN_UI)
    async def get(self):
        try:
            task_status = self.request.match_info['task_status']
            tasks = await self.delayed_task_manager.get_by_status(DelayedTaskStatus[task_status.upper()], 150)
            return {'tasks': tasks, 'task_status': task_status.upper() }
        except KeyError:
            tasks = await self.delayed_task_manager.get_by_status(DelayedTaskStatus.NEW, 150)
            return {'tasks': tasks, 'task_status': DelayedTaskStatus.NEW.name.upper() }

class AdminDelayedTasksChangeStatusView(web.View, LoggingMixin):
    """
        Change task status and redirect to new view
    """
    @set_log_marker
    @create_delayed_manager
    @require_permission(Permission.ADMIN_UI)
    async def post(self):
        uniq_md5sum = self.request.match_info['uniq_md5sum']
        data = await self.request.post()
        task_status = data['task_status']
        admin_delayed_task_list_url = self.request.app.router['admin_delayed_task_list'].url(parts={'task_status':task_status})

        delayed_tasks = await self.delayed_task_manager.get_by_uniq_md5sum(uniq_md5sum)
        await self.delayed_task_manager.clear_attempts(delayed_tasks.id)
        await self.delayed_task_manager.set_status(delayed_tasks.id, DelayedTaskStatus[task_status.upper()])

        return web.HTTPFound(admin_delayed_task_list_url)

class AdminDelayedTasksSearchView(web.View, LoggingMixin):
    """
        Search delayedtask by task_type, group, job_name, branch, sha1
    """
    @set_log_marker
    @require_permission(Permission.ADMIN_UI)
    async def post(self):
        tasks = []
        return {'tasks': tasks }
