import asyncio
import aiohttp_jinja2
import aiohttp_security
from aiohttp import web
from server.core.common import LoggingMixin
from server.core.models.delayed_tasks import DelayedTaskStatus
from server.core.security.policy import logout_and_redirect, is_authenticated, check_credentials, require_permission, Permission
from . import set_log_marker, create_delayed_manager

class LoginView(web.View, LoggingMixin):
    """
        View for login
    """
    @aiohttp_jinja2.template('login.html.j2')
    async def get(self):
        self._marker = self.request.marker
        admin_url = self.request.app.router['admin_index'].url()
        is_auth = await is_authenticated(self.request)
        if is_auth:
            response = web.HTTPFound(admin_url)
            return response
        return {}

    @aiohttp_jinja2.template('login.html.j2')
    async def post(self):
        admin_url = self.request.app.router['admin_index'].url()
        response = web.HTTPFound(admin_url)
        self._marker = self.request.marker
        post_data = await  self.request.post()
        username = post_data['username']
        password = post_data['password']
        success_auth, username = await check_credentials(self.request.app['config']['users'],
                                                        username=username,
                                                        password=password)
        if success_auth:
            await aiohttp_security.remember(self.request, response, username)
            return response

        return {'message': 'Incorrect username or password'}

class LogOutView(web.View, LoggingMixin):
    """
        View for logout
    """
    async def get(self):
        return (await logout_and_redirect(self.request))

class IndexView(web.View, LoggingMixin):
    """
        index.html
    """
    async def get(self):
        return web.FileResponse(str( self.request.app['PROJECT_ROOT']  / 'static/index.html') )

class StatsView(web.View, LoggingMixin):
    """
        Show app stats
    """
    @set_log_marker
    @create_delayed_manager
    async def get(self):
        all_running_tasks = asyncio.Task.all_tasks()
        tasks = await self.delayed_task_manager.get_by_status(DelayedTaskStatus.NEW, 150)
        stats = { 'coroutines_run' : len(all_running_tasks),
                  'task_in_queue': len(tasks),
                  'app_version': self.request.app['app_version'] }
        return web.json_response(stats)
