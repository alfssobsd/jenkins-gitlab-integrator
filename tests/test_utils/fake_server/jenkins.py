from .common import *
from .jenkins_response import *


class FakeJenkinsServer(FakeHTTPServer):
    @post('/job/{group_folder}/job/{job_name}/job/{branch}/build')
    @auth_basic_required
    async def run_build(self, request):
        group_folder = request.match_info['group_folder']
        job_name = request.match_info['job_name']
        branch = request.match_info['branch']
        raise web.HTTPCreated(text="Start")

    @get('/job/{group_folder}/job/{job_name}/job/{branch}/lastSuccessfulBuild/api/json')
    @auth_basic_required
    async def get_last_successful_build(self, request):
        group_folder = request.match_info['group_folder']
        job_name = request.match_info['job_name']
        branch = request.match_info['branch']
        fixture = None
        base_url = "http://%s:%d" % (self._server_addr, self._server_port)
        build_number = 1
        repo_url = "ssh://git@gitlab.example.local:2222/Sergey.Kravchuk/%s.git" % (job_name)
        upstream_job_name = None
        upstream_build_number = None
        if job_name == 'job_first':
            result = "SUCCESS"
            fixture = generate_last_successful_build(base_url, group_folder, job_name, branch, build_number,
                                                     upstream_job_name, upstream_build_number, repo_url, result)
        elif job_name == 'job_second':
            result = "SUCCESS"
            upstream_job_name = "job_first"
            upstream_build_number = 1
            fixture = generate_last_successful_build(base_url, group_folder, job_name, branch, build_number,
                                                     upstream_job_name, upstream_build_number, repo_url, result)
        else:
            raise web.HTTPNotFound(text="404 Not Found")
        return web.json_response(fixture)

    @get('/job/{group_folder}/job/{job_name}/job/{branch}/api/json')
    @auth_basic_required
    async def get_job_testproject_info(self, request):
        group_folder = request.match_info['group_folder']
        job_name = request.match_info['job_name']
        branch = request.match_info['branch']
        base_url = "http://%s:%d" % (self._server_addr, self._server_port)

        if job_name in ['job_first', 'job_second'] and branch in ['feature_4']:
            return web.json_response(generate_job_info(base_url, job_name))
        else:
            raise web.HTTPNotFound(text="404 Not Found")

    @get('/job/{job_name}/api/json')
    @auth_basic_required
    async def get_single_job_info(self, request):
        job_name = request.match_info['job_name']
        base_url = "http://%s:%d" % (self._server_addr, self._server_port)

        if job_name in ['job_first', 'job_second']:
            return web.json_response(generate_job_info(base_url, job_name))
        else:
            raise web.HTTPNotFound(text="404 Not Found")
