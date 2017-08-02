import pprint
import json
import asyncio
import aiohttp_jinja2
import aiohttp_security
from functools import partial
from aiohttp import web
from server.core.common import LoggingMixin, CustomEncoder
from server.core.security.policy import require_permission, Permission
from . import set_log_marker, create_delayed_manager

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
        Admin API DelayedTask v1
    """
    @set_log_marker
    @require_permission(Permission.ADMIN_UI)
    @create_delayed_manager
    async def get(self):
        #form_data = self._parse_form_data(self.request.query)
        self._logging_info(self.request.query)
        tasks = await self.delayed_task_manager.search()
        return web.json_response(tasks, dumps=partial(json.dumps, cls=CustomEncoder))
