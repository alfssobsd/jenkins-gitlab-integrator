import ujson

import aiohttp
from server.core.common import LoggingMixin

_SINGLE_JOB_FULL_PATH = '%(job_base_path)s/job/%(job_name)s'
_JOB_FULL_PATH = '%(job_base_path)s/job/%(job_name)s/job/%(branch)s'
_JOB_INFO = '%(job_full_path)s/api/json?depth=0'
_BUILD_INFO = '%(job_full_path)s/%(number)d/api/json'
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

    async def build(self, job_base_path, job_name, branch, is_multibranch=True):
        """
        Start build in Jenkins

        Args:
            job_base_path - base folder for mutibranch pipline job
            job_name - multibranch pipline job
            branch - name branch in pipline job
            is_multibranch  - multibranch or not (True or False)

        Retrun:
            Raw response data

        Exceptions:
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        job_url = self._job_url(_BUILD_JOB,
                                **{'job_full_path': self._job_full_path(job_base_path, job_name, branch, is_multibranch)})
        self._logging_info("url=%s" % job_url)

        build_parameter = { 'parameter':[] }

        #set parameter branch if it not pipline job
        if not is_multibranch:
            build_parameter['parameter'].append({
                    'name': 'branch',
                    'value': branch
                })

        data = aiohttp.FormData()
        data.add_field('json', ujson.dumps(build_parameter), content_type='text/plain')

        response_data, response_status = await self._post_form_request(job_url, data)
        self._logging_info("status = %d" % response_status)

        return response_data

    async def get_build_info(self, job_base_path, job_name, branch, repo_remote_url, build_number, is_multibranch=True):
        """
        Get info about build by number

        Args:
            job_base_path - base folder for mutibranch pipline job
            job_name - multibranch pipline job
            branch - name branch in pipline job
            repo_remote_url - repo url(for search sha1 hash)
            build_number - build number
            is_multibranch  - multibranch or not (True or False)

        Retrun:
            JenkinsBuildInfo object

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - no successful build or job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """

        job_url = self._job_url(_BUILD_INFO,
                                **{'job_full_path': self._job_full_path(job_base_path, job_name, branch, is_multibranch),
                                    'number': build_number})

        self._logging_info("url=%s" % job_url)

        response_data, response_status = await self._get_request_json(job_url)
        self._logging_info("status = %d" % response_status)

        return self._parse_build_info(response_data, repo_remote_url)

    async def get_build_numbers(self, job_base_path, job_name, branch, is_multibranch=True):
        """
        Get build numbers from job

        Args:
            job_base_path - base folder for mutibranch pipline job
            job_name - multibranch pipline job
            branch - name branch in pipline job
            is_multibranch  - multibranch or not (True or False)

        Return:
            Array [number_ids] -> [10, 9, 8, 7]

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
            KeyError - job not exist
        """

        job_url = self._job_url(_JOB_INFO,
                                **{'job_full_path': self._job_full_path(job_base_path, job_name, branch, is_multibranch)})
        self._logging_info("url=%s" % job_url)

        response_data, response_status = await self._get_request_json(job_url)
        self._logging_info("status = %d" % response_status)

        return list(map(lambda x: x['number'], response_data['builds']))

    async def get_last_success_build(self, job_base_path, job_name, branch, repo_remote_url, is_multibranch=True):
        """
        Get info about last succes build

        Args:
            job_base_path - base folder for mutibranch pipline job
            job_name - multibranch pipline job
            branch - name branch in pipline job
            repo_remote_url - repo url(for search sha1 hash)
            is_multibranch  - multibranch or not (True or False)

        Retrun:
            JenkinsBuildInfo object

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - no successful build or job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        job_url = self._job_url(_LAST_SUCCESS_BUILD_INFO,
                                **{'job_full_path': self._job_full_path(job_base_path, job_name, branch, is_multibranch)})
        self._logging_info("url=%s" % job_url)

        response_data, response_status = await self._get_request_json(job_url)
        self._logging_info("status = %d" % response_status)

        return self._parse_build_info(response_data, repo_remote_url)

    async def job_exists(self, job_base_path, job_name, branch, is_multibranch=True):
        """
        Check existence job in jenkins

        Args:
            job_base_path - base folder for mutibranch pipline job
            job_name - multibranch pipline job
            branch - name branch in pipline job
            is_multibranch  - multibranch or not (True or False)

        Return:
            raw json object

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        job_url = self._job_url(_JOB_INFO,
                                **{'job_full_path': self._job_full_path(job_base_path, job_name, branch, is_multibranch)})
        self._logging_info("url=%s" % job_url)

        response_data, response_status = await self._get_request_json(job_url)
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

    def _job_full_path(self, job_base_path, job_name, branch, is_multibranch=True):
        """
        Make full path to job

        Args:
            job_base_path - base path to job
            job_name - job_name
            branch - branch
            is_multibranch  - multibranch or not (True or False)

        Return:
            URL
        """
        if is_multibranch:
            return _JOB_FULL_PATH % {'job_base_path': job_base_path, 'job_name': job_name, 'branch': branch}

        return _SINGLE_JOB_FULL_PATH % {'job_base_path': job_base_path, 'job_name': job_name}

    async def _get_request_json(self, url):
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
        async with aiohttp.ClientSession(auth=self.basic_auth, loop=self.loop) as session:
            async with session.get(url) as resp:
                response_data = await resp.json()
                self._logging_info("status=%d" % resp.status)
                self._logging_debug("response_data=%s" % response_data)

                return response_data, resp.status

    async def _post_form_request(self, url, data):
        """
        HTTP POST FROM

        Args:
            url
            data

        Return:
            response data
            http code

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - no successful build or job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        async with aiohttp.ClientSession(auth=self.basic_auth, loop=self.loop) as session:
            async with session.post(url, data=data) as resp:
                response_data = await resp.text()
                self._logging_info("status=%d" % resp.status)
                self._logging_debug("send=%s" % data)
                self._logging_debug("response_data=%s" % response_data)

                return response_data, resp.status

    async def _post_request_json(self, url, data):
        """
        HTTP POST JSON

        Args:
            url

        Return:
            response data
            http code

        Exceptions:
            aiohttp.client_exceptions.ClientResponseError - no successful build or job not exist
            aiohttp.client_exceptions.ClientConnectorError - problem connect
        """
        async with aiohttp.ClientSession(auth=self.basic_auth, loop=self.loop) as session:
            async with session.post(url, json=data) as resp:
                response_data = await resp.json()
                self._logging_info("status=%d" % resp.status)
                self._logging_debug("send=%s" % data)
                self._logging_debug("response_data=%s" % response_data)

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
