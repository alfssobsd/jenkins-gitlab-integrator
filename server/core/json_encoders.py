import json
from server.core.models.delayed_tasks import DelayedTask
from server.core.models.jenkins_groups import JenkinsGroup

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, DelayedTask):
            return o.values
        if isinstance(o, JenkinsGroup):
            return o.values
        return json.JSONEncoder.default(self, o)
