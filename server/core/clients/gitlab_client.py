import enum
import aiohttp
from server.core.common import LoggingMixin

_PROJECT_INFO = "%(base_url)s/api/v4/projects/%(project_id)d"
_MERGE_REQUEST = "%(base_url)s/api/v4/projects/%(project_id)d/merge_requests/%(merge_id)d"
_MERGE_REQUEST_COMMENTS = "%(base_url)s/api/v4/projects/%(project_id)d/merge_requests/%(merge_id)d/notes"
_MERGE_REQUEST_COMMENT = "%(base_url)s/api/v4/projects/%(project_id)d/merge_requests/%(merge_id)d/notes/%(comment_id)d"


class GitLabMergeState(enum.Enum):
    OPENED = 1  # check and create task
    REOPENED = 2  # check and create task
    MERGED = 98  # need start push
    CLOSED = 99  # do noting


class GitLabMerge(object):
    """
    GitLab Merge info data class
    """

    def __init__(self):
        self.merge_id = 0
        self.project_id = 0
        self.target_branch = None
        self.source_branch = None
        self.state = GitLabMergeState.OPENED
        self.sha1 = None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if type(value) == GitLabMergeState:
            self._state = value
        else:
            self._state = GitLabMergeState[value.upper()]

    def __repr__(self):
        msg = "GitLabMerge project_id = %s, merge_id = %s, state = %s " % \
              (self.project_id, self.merge_id, self.state)
        msg += " target_branch = %s, source_branch = %s sha1 = %s" % \
               (self.target_branch, self.source_branch, self.sha1)
        return msg

    @staticmethod
    def from_raw_data(gitlab_raw_merge_data):
        obj = GitLabMerge()
        obj.state = gitlab_raw_merge_data['object_attributes']['state']
        obj.merge_id = gitlab_raw_merge_data['object_attributes']['iid']
        obj.project_id = gitlab_raw_merge_data['object_attributes']['target_project_id']
        obj.source_branch = gitlab_raw_merge_data['object_attributes']['source_branch']
        obj.target_branch = gitlab_raw_merge_data['object_attributes']['target_branch']
        obj.sha1 = gitlab_raw_merge_data['object_attributes']['last_commit']['id']
        return obj

    @staticmethod
    def from_api_json(json_data):
        obj = GitLabMerge()
        obj.state = json_data['state']
        obj.merge_id = json_data['iid']
        obj.project_id = json_data['project_id']
        obj.target_branch = json_data['target_branch']
        obj.source_branch = json_data['source_branch']
        obj.state = json_data['state']
        obj.sha1 = json_data['sha']

        return obj


class GitLabPush(object):
    """
    Data class for push object
    """

    def __init__(self):
        self.branch = None
        self.sha1 = None
        self.project_id = None

    def __repr__(self):
        return "branch = %s, sha1 = %s, project_id = %s" % \
               (self.branch, self.sha1, self.project_id)

    @staticmethod
    def from_push_data(gitlab_push_data):
        gitlab_push_obj = GitLabPush()
        gitlab_push_obj.branch = gitlab_push_data['ref'].replace('refs/heads/', '')
        gitlab_push_obj.sha1 = gitlab_push_data['checkout_sha']
        gitlab_push_obj.project_id = gitlab_push_data['project_id']
        return gitlab_push_obj


class GitLabClient(LoggingMixin):
    """
        Async gitlab api client
    """

    def __init__(self, marker, base_url, access_token, loop=None):
        """
            Args:
                marker - uuid marker for flow(logs)
                base_url - base url gitlab
                access_token - gitlab access token
                loop - asyncio loop, if None we get from MainThread
        """
        self._marker = marker
        self._base_url = base_url
        self._headers = {'PRIVATE-TOKEN': access_token}
        self._loop = loop

    async def get_ssh_url_to_repo(self, project_id):
        """
        Get ssh url repo from project

        Args:
            project_id - project id in gitlab

        Return:
            String

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - no successful build or job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        url = self._api_url(_PROJECT_INFO, **{'base_url': self._base_url, 'project_id': project_id})
        self._logging_info("url=%s" % url)

        data, status = await self._get_request(url)
        self._logging_info("status = %d" % status)

        return data['ssh_url_to_repo']

    async def get_merge_request(self, project_id, merge_id):
        """
        Get merge request info

        Args:
            project_id - project id
            merge_id - merge id

        Return:
            GitLabMerge

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - no successful build or job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        url = self._api_url(_MERGE_REQUEST, **{'base_url': self._base_url,
                                               'project_id': project_id, 'merge_id': merge_id})
        self._logging_info("url=%s" % url)
        data, status = await self._get_request(url)
        self._logging_info("status = %d" % status)

        return GitLabMerge.from_api_json(data)

    async def create_merge_comment(self, project_id, merge_id, message):
        """
        Create comment to merge request

        Args:
            project_id - project id
            merge_id - merge id
            message - text message

        Return:
            Int - Comment id

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - no successful build or job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        url = self._api_url(_MERGE_REQUEST_COMMENTS, **{'base_url': self._base_url,
                                                        'project_id': project_id, 'merge_id': merge_id})
        self._logging_info("url=%s" % url)
        data, status = await self._post_request(url, {'body': message})
        self._logging_info("status = %d" % status)
        self._logging_debug("create merge comment = %s" % data)
        return data['id']

    async def update_merge_comment(self, project_id, merge_id, comment_id, message):
        """
        Update comment to merge request

        Args:
            project_id - project id
            merge_id - merge id
            comment_id - comment id
            message - text message

        Return:
            Int - Comment id

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - no successful build or job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        url = self._api_url(_MERGE_REQUEST_COMMENT, **{'base_url': self._base_url,
                                                       'project_id': project_id, 'merge_id': merge_id,
                                                       'comment_id': comment_id})
        self._logging_info("url=%s" % url)
        data, status = await self._put_request(url, {'body': message})
        self._logging_info("status = %d" % status)
        self._logging_debug("update merge comment = %s" % data)
        return data['id']

    async def _get_request(self, url):
        """
        HTTP GET json

        Args:
            url
        Return:
            response data
            http code

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - no successful build or job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        async with aiohttp.ClientSession(loop=self._loop) as session:
            async with session.get(url, headers=self._headers) as resp:
                response_data = await resp.json()
                self._logging_info("status = %d" % (resp.status))
                self._logging_debug("response_data = %s" % (response_data))

                return response_data, resp.status

    async def _post_request(self, url, data):
        """
        HTTP POST json

        Args:
            url - url
            data - send hash
        Return:
            response data
            http code

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - no successful build or job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        async with aiohttp.ClientSession(loop=self._loop) as session:
            async with session.post(url, json=data, headers=self._headers) as resp:
                response_data = await resp.json()
                self._logging_info("status = %d" % (resp.status))
                self._logging_debug("send = %s" % (data))
                self._logging_debug("response_data = %s" % (response_data))

                return response_data, resp.status

    async def _put_request(self, url, data):
        """
        HTTP PUT json

        Args:
            url - url
            data - send hash
        Return:
            response data
            http code

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - no successful build or job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        async with aiohttp.ClientSession(loop=self._loop) as session:
            async with session.put(url, json=data, headers=self._headers) as resp:
                response_data = await resp.json()
                self._logging_info("status = %d" % (resp.status))
                self._logging_debug("send = %s" % (data))
                self._logging_debug("response_data = %s" % (response_data))

                return response_data, resp.status

    def _api_url(self, url_template, **kw):
        """
        Make API url

        Args:
            url_template
            kw
        Return:
            URL
        """
        return url_template % kw
