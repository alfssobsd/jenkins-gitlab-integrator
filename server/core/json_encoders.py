import json
from server.core.models.delayed_tasks import DelayedTask
from server.core.models.jenkins_groups import JenkinsGroup
from server.core.models.jenkins_jobs import JenkinsJob


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, DelayedTask):
            return o.values
        if isinstance(o, JenkinsGroup):
            return o.values
        if isinstance(o, JenkinsJob):
            return o.values
        return json.JSONEncoder.default(self, o)
