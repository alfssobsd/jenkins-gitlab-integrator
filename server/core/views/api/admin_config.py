import pprint

from aiohttp import web

from server.core.common import LoggingMixin
from server.core.security.policy import require_permission, Permission
from server.core.views import set_log_marker


class AdminApiV1ConfigView(web.View, LoggingMixin):
    """
        Admin API Config v1
    """
    @set_log_marker
    @require_permission(Permission.ADMIN_UI)
    async def get(self):
        return web.json_response( { 'body': pprint.pformat(self.request.app['config'], indent=2, width=256) } )
