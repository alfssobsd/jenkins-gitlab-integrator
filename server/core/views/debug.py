import logging

from aiohttp import web
from server.core.common import LoggingMixin
from . import set_log_marker

class DebugView(web.View, LoggingMixin):
    """
        View for debug webhooks
    """
    @set_log_marker
    async def get(self):
        request = self.request
        data = await request.text()
        self._logging_info("DebugView headers: %s, data: %s" % (request.headers, data))
        return web.Response(text="OK")

    @set_log_marker
    async def post(self):
        request = self.request
        data = await request.text()
        self._logging_info("DebugView headers: %s, data: %s" % (request.headers, data))
        return web.Response(text="OK")
