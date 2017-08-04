import pprint
import aiohttp_jinja2
from aiohttp import web
from server.core.common import LoggingMixin
from server.core.security.policy import require_permission, Permission
from server.core.models.delayed_tasks import DelayedTaskStatus
from . import set_log_marker

class AdminIndexView(web.View, LoggingMixin):
    """
        Admin index page
    """
    @set_log_marker
    @aiohttp_jinja2.template('admin/index.html.j2')
    @require_permission(Permission.ADMIN_UI)
    async def get(self):
        return { 'config': pprint.pformat(self.request.app['config'], indent=2, width=256)}
