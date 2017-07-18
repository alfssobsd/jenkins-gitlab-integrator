import pytest
import aiohttp
from server.core.clients.gitlab_client import GitLabClient, GitLabMergeState

async def test_glitab_get_ssh_url(loop, fixture_fake_gitlab_server):
    server, port = await fixture_fake_gitlab_server
    git_client = GitLabClient(marker="test_marker", base_url="http://%s:%d" %(server, port), access_token='test_token', loop=loop)
    ssh_url_to_repo = await git_client.get_ssh_url_to_repo(2)

    assert ssh_url_to_repo == 'ssh://git@gitlab.example.local:2222/Sergei.Kravchuk/project2.git'

async def test_glitab_get_merge_request(loop, fixture_fake_gitlab_server):
    server, port = await fixture_fake_gitlab_server
    gitlab_client = GitLabClient(marker="test_marker", base_url="http://%s:%d" %(server, port), access_token='test_token', loop=loop)
    project_id = 2
    merge_id = 22
    merge = await gitlab_client.get_merge_request(project_id, merge_id)
    assert merge.merge_id == merge_id
    assert merge.sha1 == "6c79b7b61e583cdeb9e2bb806c1bb77416df95e4"
    assert merge.state == GitLabMergeState.REOPENED
    assert merge.project_id == project_id
    assert merge.target_branch == "master"
    assert merge.source_branch == "feature_%d" % merge_id

async def test_gitlab_create_merge_comment(loop, fixture_fake_gitlab_server):
    server, port = await fixture_fake_gitlab_server
    gitlab_client = GitLabClient(marker="test_marker", base_url="http://%s:%d" %(server, port), access_token='test_token', loop=loop)
    project_id = 2
    merge_id = 22
    comment_id = merge_id
    return_comment_id = await gitlab_client.create_merge_comment(project_id, merge_id, "test message")

    assert return_comment_id == comment_id

async def test_gitlab_update_merge_comment(loop, fixture_fake_gitlab_server):
    server, port = await fixture_fake_gitlab_server
    gitlab_client = GitLabClient(marker="test_marker", base_url="http://%s:%d" %(server, port), access_token='test_token', loop=loop)
    project_id = 2
    merge_id = 22
    comment_id = 503
    return_comment_id = await gitlab_client.update_merge_comment(project_id, merge_id, comment_id, "test message")

    assert comment_id == return_comment_id

async def test_gitlab_fail_auth(loop, fixture_fake_gitlab_server):
    server, port = await fixture_fake_gitlab_server
    with pytest.raises(aiohttp.client_exceptions.ClientResponseError) as e_info:
        gitlab_client = GitLabClient(marker="test_marker", base_url="http://%s:%d" %(server, port), access_token='fail_token', loop=loop)
        project_id = 2
        merge_id = 22
        comment_id = 503
        return_comment_id = await gitlab_client.update_merge_comment(project_id, merge_id, comment_id, "test message")
