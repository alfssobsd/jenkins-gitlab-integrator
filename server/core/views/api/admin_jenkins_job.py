from aiohttp import web

from server.core.common import LoggingMixin


class AdminApiV1JenkinsJobListView(web.View, LoggingMixin):
    async def get(self):
        group_id = self.request.match_info['group_id']
        pass
