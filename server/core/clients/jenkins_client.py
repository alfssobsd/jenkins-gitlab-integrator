import aiohttp
from server.core.common import LoggingMixin

_JOB_FULL_PATH = '%(job_base_path)s/job/%(job_name)s/job/%(branch)s'
_JOB_INFO = '%(job_full_path)s/api/json?depth=0'
# BUILD_INFO = '%(job_full_path)s/%(number)d/api/json'
_LAST_SUCCESS_BUILD_INFO = '%(job_full_path)s/lastSuccessfulBuild/api/json'
_BUILD_JOB = '%(job_full_path)s/build'


class JenkinsBuildInfo(object):
    """
        Data class for job build info
    """

    def __init__(self):
        self.number = 0
        self.upsteram_build_number = None
        self.upsteram_project = None
        self.repo_remote_url = None
        self.sha1 = None
        self.result = None

    def __repr__(self):
        return "%s" % self.__dict__


class JenkinsClient(LoggingMixin):
    """
        Async jenkins client
    """

    def __init__(self, marker, username, password, loop=None):
        """
            Args:
                marker - uuid marker for flow(logs)
                username - user in jenkins
                password - password for user
                loop - asyncio loop, if None we get from MainThread
        """
        self.loop = loop
        self._marker = marker
        self.basic_auth = aiohttp.BasicAuth(username, password)

    async def build(self, job_base_path, job_name, branch):
        """
        Start build in Jenkins

        Args:
            job_base_path - base folder for mutibranch pipline job
            job_name - multibranch pipline job
            branch - name branch in pipline job

        Retrun:
            Raw response data

        Exceptions:
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        URL = self._job_url(_BUILD_JOB,
                            **{'job_full_path': self._job_full_path(job_base_path, job_name, branch)})
        self._logging_info("url=%s" % URL)
        data = aiohttp.FormData()
        data.add_field('json', '{"parameter": []}', content_type='text/plain')

        response_data, response_status = await self._post_form_request(URL, data)
        self._logging_info("status = %d" % response_status)

        return response_data

    async def get_last_success_build(self, job_base_path, job_name, branch, repo_remote_url):
        """
        Get info about last succes job

        Args:
            job_base_path - base folder for mutibranch pipline job
            job_name - multibranch pipline job
            branch - name branch in pipline job
            repo_remote_url - repo url(for search sha1 hash)

        Retrun:
            JenkinsBuildInfo object

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - no successful build or job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        URL = self._job_url(_LAST_SUCCESS_BUILD_INFO,
                            **{'job_full_path': self._job_full_path(job_base_path, job_name, branch)})
        self._logging_info("url=%s" % URL)

        response_data, response_status = await self._get_request_json(URL)
        self._logging_info("status = %d" % response_status)

        return self._parse_build_info(response_data, repo_remote_url)

    async def job_exists(self, job_base_path, job_name, branch):
        """
        Check existence job in jenkins

        Args:
            job_base_path - base folder for mutibranch pipline job
            job_name - multibranch pipline job
            branch - name branch in pipline job

        Return:
            raw json object

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        URL = self._job_url(_JOB_INFO,
                            **{'job_full_path': self._job_full_path(job_base_path, job_name, branch)})
        self._logging_info("url=%s" % URL)

        response_data, response_status = await self._get_request_json(URL)
        self._logging_info("status = %d" % response_status)

        return response_data

    # pirvet methods
    def _job_url(self, url_template, **kw):
        """
        Make API url

        Args:
            url_template
            kw
        Return:
            URL
        """
        return url_template % kw

    def _job_full_path(self, job_base_path, job_name, branch):
        """
        Make full path to job

        Args:
            job_base_path
            job_name
            branch

        Return:
            URL
        """
        return _JOB_FULL_PATH % {'job_base_path': job_base_path, 'job_name': job_name, 'branch': branch}

    async def _get_request_json(self, URL):
        """
        HTTP GET json

        Args:
            URL
        Return:
            response data
            http code

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - no successful build or job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        async with aiohttp.ClientSession(auth=self.basic_auth, loop=self.loop) as session:
            async with session.get(URL) as resp:
                response_data = await resp.json()
                self._logging_info("status=%d" % (resp.status))
                self._logging_debug("response_data=%s" % (response_data))

                return response_data, resp.status

    async def _post_form_request(self, URL, data):
        """
        HTTP POST FROM

        Args:
            URL
            data

        Return:
            response data
            http code

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - no successful build or job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        async with aiohttp.ClientSession(auth=self.basic_auth, loop=self.loop) as session:
            async with session.post(URL, data=data) as resp:
                response_data = await resp.text()
                self._logging_info("status=%d" % (resp.status))
                self._logging_debug("send=%s" % (data))
                self._logging_debug("response_data=%s" % (response_data))

                return response_data, resp.status

    async def _post_request_json(self, URL, data):
        """
        HTTP POST JSON

        Args:
            URL
        Return:
            response data
            http code

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - no successful build or job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        async with aiohttp.ClientSession(auth=self.basic_auth, loop=self.loop) as session:
            async with session.post(URL, json=data) as resp:
                response_data = await resp.json()
                self._logging_info("status=%d" % (resp.status))
                self._logging_debug("send=%s" % (data))
                self._logging_debug("response_data=%s" % (response_data))

                return response_data, resp.status

    def _parse_build_info(self, response, repo_remote_url):
        """
        Mapping jenkisn build info to JenkinBuildInfo

        Args:
            response - json response from jenkins
            repo_remote_url - url repo from gitlab

        Return:
            JenkinsBuildInfo
        """
        build_info = JenkinsBuildInfo()
        build_info.result = response['result']
        build_info.number = response['number']
        build_info.repo_remote_url = repo_remote_url

        for action in response['actions']:
            if '_class' in action:
                if action['_class'] == 'hudson.plugins.git.util.BuildData':
                    if action['remoteUrls'][0] == repo_remote_url:
                        build_info.sha1 = action['lastBuiltRevision']['SHA1']
                        continue
                if action['_class'] == 'hudson.model.CauseAction':
                    for cause in action['causes']:
                        if cause['_class'] == 'hudson.model.Cause$UpstreamCause':
                            build_info.upsteram_build_number = cause['upstreamBuild']
                            build_info.upsteram_project = cause['upstreamProject']
                            continue

        return build_info
