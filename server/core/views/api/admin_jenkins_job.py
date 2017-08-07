import json
from functools import partial

from aiohttp import web

from server.core.common import LoggingMixin
from server.core.json_encoders import CustomJSONEncoder
from server.core.views import create_jenkins_job_manager, set_log_marker


class AdminApiV1JenkinsJobListView(web.View, LoggingMixin):

    @set_log_marker
    @create_jenkins_job_manager
    async def get(self):
        group_id = self.request.match_info['group_id']
        jobs = await self.jenkins_job_manager.find_by_groud_id(int(group_id))
        return web.json_response(jobs, dumps=partial(json.dumps, cls=CustomJSONEncoder))
