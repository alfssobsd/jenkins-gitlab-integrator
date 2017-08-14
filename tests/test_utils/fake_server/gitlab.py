from .common import *

class FakeGitLabServer(FakeHTTPServer):

    def __init__(self, *, loop):
        super(FakeGitLabServer, self).__init__(loop=loop)
        self.STORE_WEBHOOKS = {1: list(), 2:list()}
        self.STORE_WEBHOOKS_INDEX = 1

    @get('/api/v4/projects/{project_id}')
    @auth_gilab_token_required
    async def get_project(self, request):
        project_id = request.match_info['project_id']
        fixtures = {
            1: {
                "id": 1,
                "ssh_url_to_repo": "ssh://git@gitlab.example.local:2222/Sergei.Kravchuk/project1.git"
            },
            2: {
                "id": 2,
                "ssh_url_to_repo": "ssh://git@gitlab.example.local:2222/Sergei.Kravchuk/project2.git"
            }
        }
        return web.json_response(fixtures[int(project_id)])

    @get('/api/v4/projects/{project_id}/merge_requests/{merge_id}')
    @auth_gilab_token_required
    async def get_merge_request(self, request):
        merge_id = request.match_info['merge_id']
        project_id = request.match_info['project_id']

        def generate_fixture(project_id, merge_id, state):
            return {
                "id": 100,
                "project_id": int(project_id),
                "iid": int(merge_id),
                "state": state,
                "target_branch": "master",
                "source_branch": "feature_%d" % int(merge_id),
                "sha": "6c79b7b61e583cdeb9e2bb806c1bb77416df95e4"
            }

        fixture = None
        if merge_id == 1:
            fixture = generate_fixture(project_id, merge_id, 'opened')
        elif merge_id == 2:
            fixture = generate_fixture(project_id, merge_id, 'reopened')
        if merge_id == 3:
            fixture = generate_fixture(project_id, merge_id, 'closed')
        elif merge_id == 4:
            fixture = generate_fixture(project_id, merge_id, 'merged')
        else:
            fixture = generate_fixture(project_id, merge_id, 'reopened')
        return web.json_response(fixture)

    @post('/api/v4/projects/{project_id}/merge_requests/{merge_id}/notes')
    @auth_gilab_token_required
    async def create_merge_comment(self, request):
        merge_id = request.match_info['merge_id']
        project_id = request.match_info['project_id']
        fixture = {
            "id": int(merge_id),
            "updated_at": "2017-07-07T18:18:18.176+03:00",
            "system": False,
            "body": "(🍏) SUCCESS sha:6c79b7b61e583cdeb9e2bb806c1bb77416df95e4",
            "noteable_type": "MergeRequest",
            "noteable_id": int(merge_id),
            "attachment": None,
            "author": {
                "id": 19,
                "state": "active",
                "web_url": "https://gitlab.example.local/gitlab_bot",
                "name": "gitlab_bot",
                "username": "gitlab_bot",
                "avatar_url": "https://gitlab.example.local/uploads/system/user/avatar/19/bot-512.png"
            }
        }
        return web.json_response(fixture)

    @put('/api/v4/projects/{project_id}/merge_requests/{merge_id}/notes/{noteable_id}')
    @auth_gilab_token_required
    async def update_merge_comment(self, request):
        merge_id = request.match_info['merge_id']
        project_id = request.match_info['project_id']
        noteable_id = request.match_info['noteable_id']
        fixture = {
            "id": int(noteable_id),
            "updated_at": "2017-07-07T18:18:18.176+03:00",
            "system": False,
            "body": "(🍏) SUCCESS sha:6c79b7b61e583cdeb9e2bb806c1bb77416df95e4",
            "noteable_type": "MergeRequest",
            "noteable_id": int(noteable_id),
            "attachment": None,
            "author": {
                "id": 19,
                "state": "active",
                "web_url": "https://gitlab.example.local/gitlab_bot",
                "name": "gitlab_bot",
                "username": "gitlab_bot",
                "avatar_url": "https://gitlab.example.local/uploads/system/user/avatar/19/bot-512.png"
            }
        }
        return web.json_response(fixture)

    @get('/api/v4/projects/{project_id}/hooks')
    @auth_gilab_token_required
    async def get_webhooks(self, request):
        project_id = int(request.match_info['project_id'])
        return web.json_response(self.STORE_WEBHOOKS[project_id])

    @post('/api/v4/projects/{project_id}/hooks')
    @auth_gilab_token_required
    async def create_webhook(self, request):
        project_id = int(request.match_info['project_id'])
        json_data = await request.json()

        self.STORE_WEBHOOKS_INDEX += 1
        fixture = {
            "id": self.STORE_WEBHOOKS_INDEX,
            "project_id": project_id,
            "url": json_data['url'],
            "push_events": json_data['push_events'],
            "tag_push_events": json_data['push_events'],
            "merge_requests_events": json_data['merge_requests_events'],
            "enable_ssl_verification": json_data['enable_ssl_verification'],
            "issues_events": False,
            "note_events": False,
            "pipeline_events": False,
            "wiki_page_events": False,
            "job_events":False,
            "token": json_data['token'],
            "created_at":"2017-08-14T14:32:49.797+03:00"
        }

        self.STORE_WEBHOOKS[project_id].append(fixture)
        return web.json_response(fixture, status=201)

    @delete('/api/v4/projects/{project_id}/hooks/{hook_id}')
    @auth_gilab_token_required
    async def delete_webhook(self, request):
        project_id = int(request.match_info['project_id'])
        hook_id = int(request.match_info['hook_id'])

        for index, hook_item in enumerate(self.STORE_WEBHOOKS[project_id]):
            if hook_item['id'] == hook_id:
                del self.STORE_WEBHOOKS[project_id][index]
                return web.json_response({}, status=204)

        return web.json_response({}, status=500)
