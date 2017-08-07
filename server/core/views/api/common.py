import asyncio

import aiohttp_security
from aiohttp import web

from server.core.common import LoggingMixin
from server.core.models.delayed_tasks import DelayedTaskStatus
from server.core.security.policy import check_credentials, logout
from server.core.views import set_log_marker, create_delayed_manager


class StatsApiV1View(web.View, LoggingMixin):
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

class LoginApiV1View(web.View, LoggingMixin):
    """
        Login & LogOut API
    """
    @set_log_marker
    async def post(self):
        json_data = await  self.request.json()
        username = json_data['username']
        password = json_data['password']
        success_auth, username = await check_credentials(self.request.app['config']['users'],
                                                         username=username,
                                                         password=password)
        ui_url = self.request.app.router['index_ui_root'].url()
        response = web.HTTPFound(ui_url)
        if success_auth:
            await aiohttp_security.remember(self.request, response, username)
            return web.json_response({ 'username': username })

        return web.json_response({'message': 'Incorrect username or password' }, status=401)

    @set_log_marker
    async def delete(self):
        await logout(self.request)
        return web.json_response({'message': 'logout'})
