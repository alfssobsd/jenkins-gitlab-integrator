from .common import *


class FakeGitLabServer(FakeHTTPServer):
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
